from threading import Lock
from time import monotonic_ns

import cv2
from PySide6.QtCore import QThread
from PySide6.QtGui import QImage


class CameraThread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error = None
        self._frame_lock = Lock()
        self._latest_frame = None

    def take_frame(self):
        with self._frame_lock:
            sample = self._latest_frame
            self._latest_frame = None
        return sample

    def run(self):
        capture = cv2.VideoCapture()
        try:
            if not capture.open(0):
                self.error = "No se pudo abrir la cámara. Revisa la conexión y los permisos."
                return

            while not self.isInterruptionRequested():
                ok, frame = capture.read()
                if not ok or frame is None or frame.size == 0:
                    self.error = "Se perdió la señal de la cámara. Revisa la conexión."
                    return

                captured_ns = monotonic_ns()
                height, width = frame.shape[:2]
                image = QImage(
                    frame.data, width, height, frame.strides[0], QImage.Format.Format_BGR888
                ).copy()
                with self._frame_lock:
                    self._latest_frame = (image, captured_ns)
        except cv2.error:
            self.error = "Ocurrió un error al leer la cámara."
        finally:
            capture.release()
