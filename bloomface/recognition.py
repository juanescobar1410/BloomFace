from multiprocessing import get_context
from threading import Condition
from time import monotonic_ns

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from bloomface.inference_worker import run_classifier
from bloomface.decision import GestureConfirmation, MAX_SAMPLE_GAP_NS, WAITING_FOR_GESTURE


FRAME_INTERVAL_NS = 125_000_000


class RecognitionThread(QThread):
    update = Signal(str)
    diagnostic = Signal(object)
    progress = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.error = None
        self._condition = Condition()
        self._latest_frame = None
        self._next_capture = 0
        self._stopping = False
        self._neutral_requested = False

    def calibrate_neutral(self):
        with self._condition:
            self._neutral_requested = True

    @property
    def stopping(self):
        with self._condition:
            return self._stopping

    def submit_frame(self, frame, captured_ns):
        with self._condition:
            if self._stopping or captured_ns < self._next_capture:
                return
            self._next_capture = captured_ns + FRAME_INTERVAL_NS
            self._latest_frame = (frame, captured_ns)
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
            confirmation = GestureConfirmation()
            last_update = WAITING_FOR_GESTURE
            self.update.emit(last_update)

            while True:
                sample = self._take_frame()
                if sample is None:
                    return
                frame, captured_ns = sample

                rgb = frame.convertToFormat(QImage.Format.Format_RGB888)
                message = (rgb.width(), rgb.height(), rgb.bytesPerLine(), bytes(rgb.constBits()))
                with self._condition:
                    if self._neutral_requested:
                        message = ("calibrate_neutral", message)
                        self._neutral_requested = False
                connection.send(message)
                prediction = self._receive(connection, process)
                if prediction is None:
                    return
                if prediction[0] == "error":
                    raise RuntimeError(prediction[1])
                _, gesture, face_detected, scores, milliseconds, pixels, model_label, metadata = prediction
                if self.stopping:
                    return
                if monotonic_ns() - captured_ns > MAX_SAMPLE_GAP_NS:
                    confirmation.reset()
                    state = WAITING_FOR_GESTURE
                else:
                    self.diagnostic.emit({"scores": scores, "milliseconds": milliseconds,
                                          "pixels": pixels, "face_detected": face_detected,
                                          "model_label": model_label, **metadata})
                    state = confirmation.update(gesture, face_detected, captured_ns)

                self.progress.emit(confirmation.progress)
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
