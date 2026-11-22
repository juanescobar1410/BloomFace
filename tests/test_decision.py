import unittest
from bloomface.decision import CLASSES, GestureConfirmation, NO_FACE, WAITING_FOR_GESTURE
from bloomface.metrics import classification_report


class ConfirmationTests(unittest.TestCase):
    def test_three_frames_each_class(self):
        for label in CLASSES:
            state = GestureConfirmation()
            self.assertEqual([state.update(label, True) for _ in range(4)],
                             [WAITING_FOR_GESTURE, WAITING_FOR_GESTURE, label, label])

    def test_change_requires_fresh_confirmation(self):
        state = GestureConfirmation()
        for _ in range(3):
            state.update(CLASSES[0], True)
        self.assertEqual(state.update(CLASSES[1], True), WAITING_FOR_GESTURE)
        self.assertEqual(state.update(CLASSES[0], True), WAITING_FOR_GESTURE)

    def test_face_loss_resets_even_same_gesture(self):
        state = GestureConfirmation()
        for _ in range(3):
            state.update(CLASSES[2], True)
        self.assertEqual(state.update(CLASSES[2], False), NO_FACE)
        self.assertEqual(state.update(CLASSES[2], True), WAITING_FOR_GESTURE)

    def test_pause_reset(self):
        state = GestureConfirmation()
        state.update(CLASSES[3], True)
        state.update(CLASSES[3], True)
        state.reset()
        self.assertEqual(state.update(CLASSES[3], True), WAITING_FOR_GESTURE)

    def test_invalid_class(self):
        with self.assertRaises(ValueError):
            GestureConfirmation().update("otro", True)


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
