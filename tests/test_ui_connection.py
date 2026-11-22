import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import unittest
from unittest.mock import Mock
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QComboBox
from bloomface.app import BloomFaceWindow
from bloomface.recognition import NO_FACE, WAITING_FOR_GESTURE


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

    def test_only_one_recognizer_and_four_requests_preserved(self):
        self.assertEqual(self.window.findChildren(QComboBox), [])
        for gesture in ('reposo', 'sonrisa', 'boca_abierta', 'ceno_fruncido'):
            self.recognition.update.emit(gesture)
            self.window._generator.request.assert_called_with(gesture)
        self.assertEqual(self.window._generator.request.call_count, 4)

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

    def test_diagnostic_displays_intensities_and_calibration(self):
        self.recognition.diagnostic.emit({
            'pixels': bytes(4096), 'scores': [.1, .7, .4, .05], 'milliseconds': 12.,
            'face_detected': True, 'calibrating_neutral': True,
            'neutral_message': 'Mantén el rostro relajado: 2/16 muestras.'})
        self.assertIn('no son probabilidades', self.window._signals.text())
        self.assertNotIn('%', self.window._signals.text())
        self.assertIn('2/16', self.window._recognition_status.text())
        self.recognition.update.emit(WAITING_FOR_GESTURE)
        self.assertIn('2/16', self.window._recognition_status.text())
