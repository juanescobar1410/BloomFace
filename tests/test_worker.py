import types
import unittest
from unittest.mock import patch
from PIL import Image
from bloomface.inference_worker import run_classifier


class Connection:
    def __init__(self, frame):
        self.frame = frame
        self.sent = []
        self.closed = False

    def recv(self):
        if self.frame is None:
            raise EOFError
        frame, self.frame = self.frame, None
        return frame

    def send(self, message):
        self.sent.append(message)

    def close(self):
        self.closed = True


class WorkerTests(unittest.TestCase):
    def test_rgb_stride_and_full_diagnostic_message(self):
        seen = []

        class Classifier:
            model_label = "MediaPipe Face Landmarker"
            def close(self):
                pass
            def diagnose(self, image):
                seen.append([image.getpixel((x, y)) for y in range(image.height) for x in range(image.width)])
                return {"gesture": "sonrisa", "face_detected": True,
                        "scores": [.1, .7, .1, .1], "milliseconds": 12.5,
                        "input_image": Image.new("L", (64, 64), 120)}

        # Dos filas RGB con dos bytes de padding por fila, como QImage.
        pixels = bytes([255, 0, 0, 0, 255, 0, 99, 99, 0, 0, 255, 10, 20, 30, 99, 99])
        conn = Connection((2, 2, 8, pixels))
        classifier = types.SimpleNamespace(GestureClassifier=Classifier)
        with patch.dict("sys.modules", {"bloomface.classifier": classifier}):
            run_classifier(conn)
        self.assertEqual(seen[0], [(255, 0, 0), (0, 255, 0), (0, 0, 255), (10, 20, 30)])
        self.assertEqual(conn.sent[0], "ready")
        message = conn.sent[1]
        self.assertEqual(message[:5], ("prediction", "sonrisa", True, [.1, .7, .1, .1], 12.5))
        self.assertEqual(len(message[5]), 4096)
        self.assertTrue(conn.closed)

    def test_initialization_error_is_returned_and_pipe_closed(self):
        class Classifier:
            def __init__(self):
                raise FileNotFoundError("face_landmarker.task")
        conn = Connection(None)
        with patch.dict("sys.modules", {
                         "bloomface.classifier": types.SimpleNamespace(GestureClassifier=Classifier)}):
            run_classifier(conn)
        self.assertEqual(conn.sent, [("error", "face_landmarker.task")])
        self.assertTrue(conn.closed)
