import unittest
from bloomface.decision import CLASSES, GestureConfirmation, NO_FACE, WAITING_FOR_GESTURE
from bloomface.metrics import classification_report


class ConfirmationTests(unittest.TestCase):
    def setUp(self):
        self.state = GestureConfirmation()

    def update(self, gesture, milliseconds, face_detected=True):
        return self.state.update(gesture, face_detected, milliseconds * 1_000_000)

    def test_first_sample_at_three_seconds_or_later_confirms(self):
        for label, final_sample in zip(CLASSES, (3000, 3001, 3050, 3000)):
            with self.subTest(label=label):
                self.state.reset()
                for time_ms in (0, 750, 1500, 2250, 2990):
                    self.assertEqual(self.update(label, time_ms), WAITING_FOR_GESTURE)
                self.assertEqual(self.update(label, final_sample), label)

    def test_progress_reaches_full_only_on_confirmation_and_resets(self):
        for time_ms in (0, 750, 1500, 2250, 2990):
            self.assertEqual(self.update("sonrisa", time_ms), WAITING_FOR_GESTURE)
            self.assertAlmostEqual(self.state.progress, time_ms / 3000)
        self.assertEqual(self.update("sonrisa", 3000), "sonrisa")
        self.assertEqual(self.state.progress, 1.0)
        self.assertEqual(self.update(None, 3100), WAITING_FOR_GESTURE)
        self.assertEqual(self.state.progress, 0.0)

    def test_change_requires_fresh_confirmation(self):
        self.assertEqual(self.update("reposo", 0), WAITING_FOR_GESTURE)
        self.assertEqual(self.update("reposo", 1000), WAITING_FOR_GESTURE)
        self.assertEqual(self.update("reposo", 2000), WAITING_FOR_GESTURE)
        for time_ms in (2900, 3900, 4900, 5890):
            self.assertEqual(self.update("sonrisa", time_ms), WAITING_FOR_GESTURE)
        self.assertEqual(self.update("sonrisa", 5900), "sonrisa")

    def test_no_face_and_pause_reset(self):
        for end_attempt in ("no_face", "pause"):
            with self.subTest(end_attempt=end_attempt):
                self.state.reset()
                for time_ms in (0, 1000, 2000, 2990):
                    self.assertEqual(self.update("boca_abierta", time_ms), WAITING_FOR_GESTURE)
                if end_attempt == "no_face":
                    self.assertEqual(self.update(None, 2995, face_detected=False), NO_FACE)
                else:
                    self.state.reset()
                for time_ms in (3000, 4000, 5000, 5990):
                    self.assertEqual(self.update("boca_abierta", time_ms), WAITING_FOR_GESTURE)
                self.assertEqual(self.update("boca_abierta", 6000), "boca_abierta")

    def test_silence_between_samples_does_not_confirm(self):
        self.assertEqual(self.update("sonrisa", 0), WAITING_FOR_GESTURE)
        self.assertEqual(self.update("sonrisa", 3000), WAITING_FOR_GESTURE)
        for time_ms in (4000, 5000, 5990):
            self.assertEqual(self.update("sonrisa", time_ms), WAITING_FOR_GESTURE)
        self.assertEqual(self.update("sonrisa", 6000), "sonrisa")

    def test_invalid_class(self):
        with self.assertRaises(ValueError):
            self.update("otro", 0)


class MetricTests(unittest.TestCase):
    def test_perfect_balanced(self):
        report = classification_report(list(CLASSES), list(CLASSES))
        self.assertEqual(report["f1_macro_4_classes"], 1)
        self.assertEqual(report["rejections"], 0)

    def test_rejections_reduce_recall_and_accuracy(self):
        report = classification_report(list(CLASSES), [CLASSES[0], CLASSES[1], None, CLASSES[3]])
        self.assertEqual(report["recall"][CLASSES[2]], 0)
        self.assertEqual(report["accuracy_including_rejections"], .75)
        self.assertEqual(report["rejections"], 1)

    def test_smile_open_mouth_confusion(self):
        report = classification_report([CLASSES[1], CLASSES[2]], [CLASSES[2], CLASSES[2]])
        self.assertEqual(report["confusion_matrix"][1][2], 1)
        self.assertEqual(report["recall"][CLASSES[1]], 0)
        self.assertEqual(report["recall"][CLASSES[2]], 1)


if __name__ == "__main__":
    unittest.main()
