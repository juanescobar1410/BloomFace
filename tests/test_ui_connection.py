import base64
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import unittest
from unittest.mock import Mock, call, patch
from PySide6.QtCore import QBuffer, QIODevice, QObject, QProcess, Signal
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox
from bloomface.app import BloomFaceWindow
from bloomface.camera_preview import CameraPreview
from bloomface.composition_view import PLACEHOLDER
from bloomface.decision import NO_FACE, WAITING_FOR_GESTURE
from bloomface.recognition import RecognitionThread


class RecognitionSignals(QObject):
    update = Signal(str)
    diagnostic = Signal(object)
    stopping = False

    def calibrate_neutral(self):
        pass

    def stop(self):
        self.stopping = True


class ConnectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = BloomFaceWindow()
        self.recognition = RecognitionSignals(self.window)
        self.window._recognition = self.recognition
        self.recognition.update.connect(self.window._handle_recognition_update)
        self.recognition.diagnostic.connect(self.window._show_diagnostic)
        self.window._generator.request = Mock()
        self.window._generator.invalidate = Mock()

    def tearDown(self):
        self.window._recognition = None
        self.window.close()

    def test_three_seconds_to_request_each_flower_without_duplicates(self):
        self.assertEqual(self.window.findChildren(QComboBox), [])
        frame = QImage(8, 8, QImage.Format.Format_RGB888)
        frame.fill(0)
        gestures = ("reposo", "sonrisa", "boca_abierta", "ceno_fruncido")
        original_start_button = self.window._start_recognition_button
        self.window._camera_has_frame = True

        for index, gesture in enumerate(gestures):
            recognizer = RecognitionThread(self.window)
            self.window._recognition = recognizer
            recognizer.update.connect(self.window._handle_recognition_update)
            recognizer.progress.connect(self.window._show_gesture_progress)
            elapsed = iter((0, 750, 1500, 2250, 2990, 3000, 3500))
            captured_ns = 0

            def take_frame():
                nonlocal captured_ns
                time_ms = next(elapsed, None)
                if time_ms is None:
                    return None
                count = index + int(time_ms > 3000)
                self.assertEqual(self.window._generator.request.call_args_list,
                                 [call(label) for label in gestures[:count]])
                captured_ns = time_ms * 1_000_000
                return frame, captured_ns

            prediction = ("prediction", gesture, True, (), 0, None, "fake", {})
            with (patch("bloomface.recognition.get_context") as context,
                  patch("bloomface.recognition.monotonic_ns", side_effect=lambda: captured_ns),
                  patch.object(recognizer, "_take_frame", side_effect=take_frame),
                  patch.object(recognizer, "_receive", side_effect=("ready",) + (prediction,) * 7)):
                context.return_value.Pipe.return_value = Mock(), Mock()
                context.return_value.Process.return_value.pid = None
                recognizer.run()

            self.assertIsNone(recognizer.error)
            self.assertEqual(self.window._generator.request.call_args_list,
                             [call(label) for label in gestures[:index + 1]])
            self.assertEqual(self.window._flower_view.loading, index == 0)
            if index == 0:
                self.assertEqual(len(self.window._flower_view._petals), 8)
            self.window._generator.image_ready.emit(frame, 1.0)
            self.assertFalse(self.window._flower_view.loading)
            self.assertFalse(self.window._flower_view.pixmap().isNull())
            self.assertTrue(self.window._paused)
            self.assertTrue(recognizer.stopping)
            self.assertIs(self.window._start_recognition_button, original_start_button)
            self.assertGreaterEqual(self.window._paused_actions_layout.indexOf(original_start_button), 0)
            self.assertTrue(self.window._resume_button.isHidden())

            self.window._recognition = None
            with patch.object(self.window, "_start_recognition") as restart:
                original_start_button.click()
                restart.assert_called_once_with()
            self.assertFalse(self.window._paused)
            self.assertEqual(self.window._preview._progress, 0.0)
            self.assertGreaterEqual(self.window._preview_actions_layout.indexOf(original_start_button), 0)

    def test_first_flower_loader_survives_fallback_and_stops_on_failure_or_pause(self):
        self.window._camera_has_frame = True
        view = self.window._flower_view
        self.assertEqual(view.text(), PLACEHOLDER)
        self.window._generator.status.emit("Cargando generador floral en GPU…")
        self.assertFalse(view.loading)

        self.recognition.update.emit("sonrisa")
        self.assertTrue(view.loading)
        self.window._generator.status.emit("GPU no disponible. Cargando generador en CPU…")
        self.assertTrue(view.loading)
        self.window._generator.failed.emit("No se obtuvo una acuarela utilizable.")
        self.assertTrue(self.window._paused)
        self.assertFalse(view.loading)
        self.assertEqual(view.text(), PLACEHOLDER)

        self.window._recognition = None
        self.window._camera_has_frame = True
        with patch.object(self.window, "_start_recognition") as restart:
            self.window._start_recognition_button.click()
            restart.assert_called_once_with()
        recognition = RecognitionSignals(self.window)
        self.window._recognition = recognition
        recognition.update.connect(self.window._handle_recognition_update)
        recognition.update.emit("reposo")
        self.assertTrue(view.loading)

        self.window._pause.click()
        self.assertTrue(self.window._paused)
        self.assertFalse(view.loading)
        self.assertEqual(view.text(), PLACEHOLDER)

    def test_first_flower_loader_stops_on_close(self):
        self.recognition.update.emit("sonrisa")
        self.assertTrue(self.window._flower_view.loading)
        self.window.close()
        self.assertFalse(self.window._flower_view.loading)

    def test_camera_border_starts_at_bottom_and_joins_at_top_when_ready(self):
        preview = CameraPreview("")
        preview.resize(420, 270)
        preview.setStyleSheet("background-color: #dedfce; border-radius: 8px;")
        preview.show()
        self.app.processEvents()
        baseline = preview.grab().toImage()
        preview.set_gesture_progress(0.20)
        preview._transition.setCurrentTime(preview._transition.duration())
        early = preview.grab().toImage()
        self.assertNotEqual(early.pixelColor(200, 266), baseline.pixelColor(200, 266))
        self.assertNotEqual(early.pixelColor(220, 266), baseline.pixelColor(220, 266))
        self.assertEqual(early.pixelColor(210, 4), baseline.pixelColor(210, 4))

        preview.set_gesture_progress(0.55)
        preview._transition.setCurrentTime(preview._transition.duration())
        halfway = preview.grab().toImage()
        left = halfway.pixelColor(4, 170)
        right = halfway.pixelColor(415, 170)
        self.assertEqual(left, QColor("#96336f"))
        self.assertEqual(right, QColor("#d27579"))
        self.assertEqual(halfway.pixelColor(210, 4), baseline.pixelColor(210, 4))

        preview.set_gesture_progress(1.0)
        complete = preview.grab().toImage()
        self.assertEqual(complete.pixelColor(210, 4), QColor("#29c56f"))
        preview.set_gesture_progress(0.0)
        self.assertEqual(preview.grab().toImage().pixelColor(210, 266), baseline.pixelColor(210, 266))
        preview.close()

    def test_new_gesture_is_ignored_until_the_next_round(self):
        self.recognition.update.emit("sonrisa")
        self.recognition.update.emit("boca_abierta")
        self.recognition.update.emit(NO_FACE)

        self.window._generator.request.assert_called_once_with("sonrisa")
        self.window._generator.invalidate.assert_not_called()
        self.assertFalse(self.window._paused)

    def test_delayed_result_cannot_confirm_old_frame(self):
        recognizer = RecognitionThread(self.window)
        self.window._recognition = recognizer
        recognizer.update.connect(self.window._handle_recognition_update)
        frame = QImage(8, 8, QImage.Format.Format_RGB888)
        frame.fill(0)
        milliseconds = (0, 1000, 2000, 2990, 3000)
        frames = [(frame, ms * 1_000_000) for ms in milliseconds] + [None]
        responses = ("ready",) + (("prediction", "sonrisa", True, (), 0, None, "fake", {}),) * 5
        now_ns = [ms * 1_000_000 for ms in (*milliseconds[:-1], 4200)]
        with (patch("bloomface.recognition.get_context") as context,
              patch("bloomface.recognition.monotonic_ns", side_effect=now_ns),
              patch.object(recognizer, "_take_frame", side_effect=frames),
              patch.object(recognizer, "_receive", side_effect=responses)):
            context.return_value.Pipe.return_value = Mock(), Mock()
            context.return_value.Process.return_value.pid = None
            recognizer.run()

        self.assertIsNone(recognizer.error)
        self.window._generator.request.assert_not_called()

    def test_only_current_flower_reaches_the_composition(self):
        self.recognition.update.emit("sonrisa")
        generator = self.window._generator
        generator._request_id = 2
        generator._inflight = {"id": 1, "gesture": "reposo"}
        png = QBuffer()
        png.open(QIODevice.OpenModeFlag.WriteOnly)
        image = QImage(2, 2, QImage.Format.Format_RGB32)
        image.fill(0xff00aa00)
        self.assertTrue(image.save(png, "PNG"))
        encoded = base64.b64encode(bytes(png.data())).decode("ascii")

        generator._handle_result({"id": 1, "image": encoded, "seconds": 1})
        self.assertIsNone(self.window._generated)

        generator._inflight = {"id": 2, "gesture": "sonrisa"}
        generator._handle_result({"id": 2, "image": encoded, "seconds": 1})
        self.assertEqual(self.window._generated.pixelColor(0, 0).green(), 170)

    def test_preview_uses_automatic_backend_without_a_checkbox(self):
        self.assertEqual(self.window._preview_actions_layout.parentWidget().findChildren(QCheckBox), [])
        self.assertEqual(self.window._generator._backend, "gpu")

    def test_gpu_failure_retries_the_current_flower_on_cpu(self):
        generator = self.window._generator
        generator.start = Mock()
        generator._request_id = 1
        gesture = {"id": 1, "gesture": "sonrisa"}
        generator._inflight = gesture
        generator._exited(1, QProcess.ExitStatus.CrashExit)
        self.assertEqual(generator._backend, "cpu")
        self.assertEqual(generator._pending, gesture)
        generator.start.assert_called_once()

        generator._exited(1, QProcess.ExitStatus.CrashExit)
        generator.start.assert_called_once()

    def test_gpu_failure_uses_newest_request_and_respects_invalidation(self):
        generator = self.window._generator
        generator.start = Mock()
        old = {"id": 1, "gesture": "reposo"}
        latest = {"id": 2, "gesture": "boca_abierta"}
        generator._inflight = old
        generator._pending = latest
        generator._request_id = 2
        generator._exited(1, QProcess.ExitStatus.CrashExit)
        self.assertEqual(generator._pending, latest)

        generator._backend = "gpu"
        generator._inflight = latest
        generator._request_id = 3  # Un cambio de rostro o una pausa invalidó la solicitud.
        generator._pending = None
        generator._exited(1, QProcess.ExitStatus.CrashExit)
        self.assertIsNone(generator._pending)

    def test_flower_rejected_by_filter_allows_another_round_without_switching_backend(self):
        self.recognition.update.emit("reposo")
        previous = QImage(2, 2, QImage.Format.Format_RGB32)
        previous.fill(0)
        self.window._generated = previous
        generator = self.window._generator
        generator._request_id = 1
        generator._inflight = {"id": 1, "gesture": "reposo"}
        generator._handle_result({"id": 1, "error": "No se obtuvo una acuarela utilizable."})
        self.assertEqual(generator._backend, "gpu")
        self.assertIn("acuarela utilizable", self.window._status_message.text())
        self.assertIs(self.window._generated, previous)
        self.assertTrue(self.window._paused)
        self.assertEqual(self.window._view_state, "next_flower")

    def test_absent_and_ambiguous_never_request_a_flower(self):
        self.recognition.update.emit(NO_FACE)
        self.window._generator.invalidate.assert_called_once()
        self.recognition.update.emit(WAITING_FOR_GESTURE)
        self.window._generator.request.assert_not_called()

    def test_adjust_neutral_stays_in_existing_worker(self):
        self.recognition.calibrate_neutral = Mock()
        self.window._calibrate_neutral()
        self.recognition.calibrate_neutral.assert_called_once()
        self.assertTrue(self.window._neutral_calibrating)
        self.window._generator.invalidate.assert_called_once()
        self.assertFalse(self.recognition.stopping)

    def test_pause_and_resume_preserve_lifecycle(self):
        self.window._toggle_pause()
        self.assertTrue(self.recognition.stopping)
        self.assertTrue(self.window._paused)
        self.window._generator.invalidate.assert_called_once()
        self.window._recognition = None
        self.window._toggle_pause()
        self.assertFalse(self.window._paused)
        self.assertIsNone(self.window._recognition)

    def test_diagnostic_preserves_calibration_message(self):
        self.recognition.diagnostic.emit({
            'pixels': bytes(4096), 'scores': [.1, .7, .4, .05], 'milliseconds': 12.,
            'face_detected': True, 'calibrating_neutral': True,
            'neutral_message': 'Mantén el rostro relajado: 2/16 muestras.'})
        self.assertIn('16 muestras', self.window._status_message.text())
        self.recognition.update.emit(WAITING_FOR_GESTURE)
        self.assertIn('16 muestras', self.window._status_message.text())


if __name__ == '__main__':
    unittest.main()
