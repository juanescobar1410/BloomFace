from multiprocessing import get_context
from threading import Condition
from time import monotonic

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from bloomface.inference_worker import run_classifier


CONFIRMATION_FRAMES = 3
FRAME_INTERVAL_SECONDS = 0.125
WAITING_FOR_GESTURE = "waiting"
NO_FACE = "no_face"


class RecognitionThread(QThread):
    update = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.error = None
        self._condition = Condition()
        self._latest_frame = None
        self._next_capture = 0.0
        self._stopping = False

    @property
    def stopping(self):
        with self._condition:
            return self._stopping

    def submit_frame(self, frame):
        now = monotonic()
        with self._condition:
            if self._stopping or now < self._next_capture:
                return
            self._next_capture = now + FRAME_INTERVAL_SECONDS
            self._latest_frame = frame
            self._condition.notify()

    def stop(self):
        with self._condition:
            self._stopping = True
            self._latest_frame = None
            self._condition.notify()

    def _take_frame(self):
        with self._condition:
            self._condition.wait_for(lambda: self._stopping or self._latest_frame is not None)
            frame = self._latest_frame
            self._latest_frame = None
        return frame

    def _receive(self, connection, process):
        while not self.stopping:
            if connection.poll(0.1):
                try:
                    return connection.recv()
                except EOFError as error:
                    raise RuntimeError("Se cerró el proceso del clasificador.") from error
            if not process.is_alive():
                raise RuntimeError("Se cerró el proceso del clasificador.")
        return None

    def run(self):
        context = get_context("spawn")
        connection, child_connection = context.Pipe()
        process = context.Process(target=run_classifier, args=(child_connection,), daemon=True)
        try:
            process.start()
            child_connection.close()
            ready = self._receive(connection, process)
            if ready is None:
                return
            if ready != "ready":
                raise RuntimeError(ready[1])
            candidate = None
            repetitions = 0
            last_update = WAITING_FOR_GESTURE
            self.update.emit(last_update)

            while True:
                frame = self._take_frame()
                if frame is None:
                    return

                rgb = frame.convertToFormat(QImage.Format.Format_RGB888)
                connection.send(
                    (rgb.width(), rgb.height(), rgb.bytesPerLine(), bytes(rgb.constBits()))
                )
                prediction = self._receive(connection, process)
                if prediction is None:
                    return
                if prediction[0] == "error":
                    raise RuntimeError(prediction[1])
                _, gesture, face_detected = prediction
                if not face_detected:
                    candidate = None
                    repetitions = 0
                    state = NO_FACE
                else:
                    if gesture != candidate:
                        candidate = gesture
                        repetitions = 0
                    repetitions = min(repetitions + 1, CONFIRMATION_FRAMES)
                    state = gesture if repetitions == CONFIRMATION_FRAMES else WAITING_FOR_GESTURE

                if state != last_update:
                    self.update.emit(state)
                    last_update = state
        except Exception as error:
            self.error = str(error) or type(error).__name__
        finally:
            connection.close()
            child_connection.close()
            if process.pid is not None:
                process.join(timeout=0.5)
                if process.is_alive():
                    process.terminate()
                    process.join()
            process.close()
