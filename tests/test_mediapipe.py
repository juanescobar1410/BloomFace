import json
import io
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
import types
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
from bloomface.classifier import BlendshapeDecision, FEATURES, GestureClassifier as MediaPipeGestureClassifier
from bloomface.decision import GestureConfirmation, WAITING_FOR_GESTURE, NO_FACE
from bloomface.mediapipe_assets import ensure_model, valid_bundle


def signals(smile=0., jaw=0., brow=0.):
    return dict(zip(FEATURES, (smile, smile, jaw, brow, brow)))


class DecisionTests(unittest.TestCase):
    def test_four_states_and_smiling_open_mouth(self):
        decision = BlendshapeDecision()
        for raw, expected in [(signals(), 'reposo'), (signals(smile=.8), 'sonrisa'),
                              (signals(jaw=.8), 'boca_abierta'), (signals(brow=.7), 'ceno_fruncido'),
                              (signals(smile=.8, jaw=.8), 'sonrisa')]:
            self.assertEqual(decision.decide(raw)[0], expected)

    def test_ambiguous_and_unilateral_brow(self):
        decision = BlendshapeDecision()
        self.assertIsNone(decision.decide(signals(smile=.35))[0])
        self.assertIsNone(decision.decide(signals(smile=.8, brow=.7))[0])
        raw = signals()
        raw['browDownLeft'] = .9
        self.assertNotEqual(decision.decide(raw)[0], 'ceno_fruncido')

    def test_neutral_reference_and_invalid_values(self):
        raw = signals(brow=.6)
        self.assertEqual(BlendshapeDecision(raw).decide(raw)[0], 'reposo')
        with self.assertRaises(ValueError):
            BlendshapeDecision().decide(signals(jaw=float('nan')))
        with self.assertRaises(ValueError):
            BlendshapeDecision(signals(jaw=1.))

    def test_rejection_breaks_confirmation(self):
        confirm = GestureConfirmation(3)
        confirm.update('sonrisa', True)
        confirm.update('sonrisa', True)
        self.assertEqual(confirm.update(None, True), WAITING_FOR_GESTURE)
        self.assertEqual(confirm.update('sonrisa', True), WAITING_FOR_GESTURE)
        self.assertEqual(confirm.update(None, False), NO_FACE)


class AdapterTests(unittest.TestCase):
    def test_rgb_input_timestamps_neutral_and_no_face(self):
        # Doble del SDK: prueba integración y formato, no precisión del modelo real.
        seen, options_seen = [], []
        raw = signals(brow=.5)
        face_result = types.SimpleNamespace(
            face_landmarks=[[types.SimpleNamespace(x=.2, y=.2), types.SimpleNamespace(x=.8, y=.8)]],
            face_blendshapes=[[types.SimpleNamespace(category_name=k, score=v) for k, v in raw.items()]])
        class Landmarker:
            result = face_result
            closed = False
            def detect_for_video(self, image, timestamp):
                seen.append((image.data.copy(), timestamp))
                return self.result
            def close(self):
                self.closed = True
            def detect(self, image):
                return self.result
        landmarker = Landmarker()
        class BaseOptions:
            Delegate = types.SimpleNamespace(CPU='cpu')
            def __init__(self, **kw):
                self.kw = kw
        def make_options(**kw):
            options_seen.append(kw)
            return kw
        mp = types.ModuleType('mediapipe')
        mp.ImageFormat = types.SimpleNamespace(SRGB='srgb')
        mp.Image = lambda **kw: types.SimpleNamespace(**kw)
        tasks = types.ModuleType('mediapipe.tasks')
        python = types.ModuleType('mediapipe.tasks.python')
        vision = types.ModuleType('mediapipe.tasks.python.vision')
        tasks.python = python
        python.BaseOptions = BaseOptions
        python.vision = vision
        vision.RunningMode = types.SimpleNamespace(VIDEO='video', IMAGE='image')
        vision.FaceLandmarkerOptions = make_options
        vision.FaceLandmarker = types.SimpleNamespace(create_from_options=lambda opts: landmarker)
        modules = {'mediapipe': mp, 'mediapipe.tasks': tasks,
                   'mediapipe.tasks.python': python, 'mediapipe.tasks.python.vision': vision}
        with TemporaryDirectory() as directory, patch.dict('sys.modules', modules):
            model = Path(directory) / 'model.task'
            model.write_bytes(b'test double')
            reference = Path(directory) / 'reposo.json'
            classifier = MediaPipeGestureClassifier(model, reference)
            image = Image.new('RGB', (800, 600), (240, 20, 10))
            first = classifier.diagnose(image)
            self.assertEqual(first['gesture'], 'ceno_fruncido')
            self.assertEqual(first['score_kind'], 'intensidades')
            self.assertEqual(first['input_image'].size, (64, 64))
            self.assertEqual(seen[0][0].shape, (480, 640, 3))
            np.testing.assert_array_equal(seen[0][0][0, 0], [240, 20, 10])
            self.assertTrue(options_seen[0]['output_face_blendshapes'])
            classifier.begin_neutral_calibration()
            landmarker.result = types.SimpleNamespace(face_landmarks=[], face_blendshapes=[])
            absent = classifier.diagnose(image)
            self.assertFalse(absent['face_detected'])
            self.assertFalse(reference.exists())
            landmarker.result = face_result
            for _ in range(16):
                result = classifier.diagnose(image)
                self.assertIsNone(result['gesture'])
            self.assertFalse(result['calibrating_neutral'])
            self.assertEqual(json.loads(reference.read_text())['neutral']['browDownLeft'], .5)
            self.assertEqual(classifier.diagnose(image)['gesture'], 'reposo')
            self.assertTrue(all(b[1] > a[1] for a, b in zip(seen, seen[1:])))
            classifier.close()
            self.assertTrue(landmarker.closed)
            photos = MediaPipeGestureClassifier(model, reference, running_mode='image')
            self.assertEqual(options_seen[-1]['running_mode'], 'image')
            self.assertEqual(photos.diagnose(image)['gesture'], 'reposo')
            photos.close()


class AssetTests(unittest.TestCase):
    def test_bundle_download_validation_and_reuse(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, 'w') as archive:
            for name in ('face_detector.tflite', 'face_landmarks_detector.tflite', 'face_blendshapes.tflite'):
                archive.writestr(name, b'test double, not a real model')
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'face_landmarker.task'
            with patch('urllib.request.urlopen', return_value=io.BytesIO(data.getvalue())) as download:
                ensure_model(path)
                self.assertTrue(valid_bundle(path))
                ensure_model(path, check_only=True)
                self.assertEqual(download.call_count, 1)
                self.assertEqual(len(json.loads(path.with_suffix('.json').read_text())['sha256']), 64)

    def test_bad_download_never_becomes_ready(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'face_landmarker.task'
            with patch('urllib.request.urlopen', side_effect=lambda *a, **k: io.BytesIO(b'error page')):
                with self.assertRaises(RuntimeError):
                    ensure_model(path)
            self.assertFalse(path.exists())
            self.assertFalse(path.with_suffix('.download').exists())
            with self.assertRaises(FileNotFoundError):
                ensure_model(path, check_only=True)

