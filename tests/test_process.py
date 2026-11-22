"""Prueba con SDK y modelo reales, sin abrir la cámara ni afirmar precisión."""
import importlib.util
from multiprocessing import get_context
import unittest

from bloomface.classifier import MODEL_PATH
from bloomface.inference_worker import run_classifier


@unittest.skipUnless(importlib.util.find_spec('mediapipe') and MODEL_PATH.is_file(),
                     'Completa primero la preparación de MediaPipe.')
class RealWorkerTests(unittest.TestCase):
    def test_real_model_child_process_no_face_and_clean_shutdown(self):
        ctx = get_context('spawn')
        parent, child = ctx.Pipe()
        process = ctx.Process(target=run_classifier, args=(child,))
        process.start()
        child.close()
        try:
            self.assertTrue(parent.poll(30), 'El modelo no terminó de cargar.')
            self.assertEqual(parent.recv(), 'ready')
            frame = (256, 256, 768, bytes(256 * 256 * 3))
            parent.send(frame)
            self.assertTrue(parent.poll(20), 'Sin respuesta de inferencia.')
            result = parent.recv()
            self.assertEqual(result[0], 'prediction')
            self.assertIsNone(result[1])
            self.assertFalse(result[2])
            self.assertEqual(result[6], 'MediaPipe Face Landmarker')
            self.assertEqual(result[7]['score_kind'], 'intensidades')
            parent.send(('calibrate_neutral', frame))
            self.assertTrue(parent.poll(20))
            result = parent.recv()
            self.assertTrue(result[7]['calibrating_neutral'])
            self.assertFalse(result[2])
        finally:
            parent.close()
            process.join(5)
            if process.is_alive():
                process.terminate()
                process.join(5)
            code = process.exitcode
            process.close()
        self.assertEqual(code, 0)
