import base64
import json
import os
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, QTimer, Signal
from PySide6.QtGui import QImage


class FloralProcess(QObject):
    status = Signal(str)
    image_ready = Signal(QImage, float)
    failed = Signal(str)
    stopped = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._read_messages)
        self._process.readyReadStandardError.connect(self._read_diagnostics)
        self._process.finished.connect(self._exited)
        self._process.errorOccurred.connect(self._process_error)
        self._gpu_timeout = QTimer(self)
        self._gpu_timeout.setSingleShot(True)
        self._gpu_timeout.setInterval(120_000)
        self._gpu_timeout.timeout.connect(self._gpu_timed_out)
        self._backend = "gpu"
        source_root = Path(__file__).resolve().parents[1]
        if getattr(sys, "frozen", False):
            self._root = Path(sys.executable).resolve().parent / "floral_runtime"
        else:
            runtime = os.environ.get("BLOOMFACE_FLORAL_RUNTIME")
            self._root = Path(runtime).expanduser().resolve() if runtime else source_root / "floral_runtime"
        self._notebook = source_root / "notebooks" / "BloomFace_Generacion_Floral.ipynb"
        self._buffer = bytearray()
        self._diagnostics = b""
        self._failure_detail = ""
        self._ready = False
        self._closing = False
        self._pending = None
        self._inflight = None
        self._request_id = 0

    @property
    def running(self):
        return self._process.state() != QProcess.ProcessState.NotRunning

    def start(self, status_message=None):
        if self.running or self._closing or (self._backend == "gpu" and self._failure_detail):
            return
        python = self._root / "python" / "python.exe"
        if not python.is_file() and not getattr(sys, "frozen", False):
            python = self._root / "venv" / "Scripts" / "python.exe"
        weights = self._root / "weights"
        model_dirs_present = all((weights / name).is_dir() for name in ("sd15", "scribble", "lcm"))
        if not python.is_file() or not model_dirs_present or not self._notebook.is_file():
            self._pending = None
            self._report_failure("Faltan archivos del generador floral. Abre BloomFace desde la carpeta completa.")
            return
        self._buffer.clear()
        self._diagnostics = b""
        self._failure_detail = ""
        self._ready = False
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert("HF_HUB_OFFLINE", "1")
        environment.insert("TRANSFORMERS_OFFLINE", "1")
        environment.insert("PYTHONUTF8", "1")
        environment.insert("OMP_NUM_THREADS", "2")
        environment.insert("MKL_NUM_THREADS", "2")
        self._process.setProcessEnvironment(environment)
        worker = Path(__file__).with_name("floral_worker.py")
        self.status.emit(status_message or f"Cargando generador floral en {self._backend.upper()}…")
        if self._backend == "gpu":
            self._gpu_timeout.start()
        self._process.start(
            str(python), ["-I", "-B", "-u", str(worker), str(self._notebook), str(weights), self._backend],
        )

    def request(self, gesture):
        if self._closing:
            return
        self._request_id += 1
        self._pending = {"id": self._request_id, "gesture": gesture}
        if self._inflight is not None:
            self.status.emit("Generando acuarela… Se usará el gesto más reciente.")
        elif self.running and not self._ready:
            self.status.emit(f"Cargando generador floral en {self._backend.upper()}…")
        self.start()
        self._dispatch()

    def invalidate(self):
        self._request_id += 1
        self._pending = None

    def close(self):
        self._closing = True
        self.invalidate()
        if self.running:
            self._process.kill()

    def _dispatch(self):
        if not self.running or not self._ready or self._inflight is not None or self._pending is None:
            return
        self._inflight = self._pending
        payload = json.dumps(self._pending).encode("utf-8") + b"\n"
        self._pending = None
        self.status.emit(f"Generando acuarela en {self._backend.upper()}…")
        if self._backend == "gpu":
            self._gpu_timeout.start()
        self._process.write(payload)

    def _read_messages(self):
        self._buffer.extend(bytes(self._process.readAllStandardOutput()))
        while b"\n" in self._buffer:
            raw, _, rest = self._buffer.partition(b"\n")
            self._buffer = rest
            try:
                message = json.loads(raw)
            except (UnicodeError, ValueError):
                continue
            if self._closing or self._failure_detail:
                continue
            if message.get("ready"):
                self._gpu_timeout.stop()
                self._ready = True
                if self._pending is None:
                    self.status.emit(f"Generador listo · {self._backend.upper()}")
                self._dispatch()
            elif "fatal" in message:
                self._failure_detail = message["fatal"]
                self._ready = False
            elif "id" in message:
                self._handle_result(message)

    def _handle_result(self, message):
        if self._inflight is None or message["id"] != self._inflight["id"]:
            return
        self._gpu_timeout.stop()
        self._inflight = None
        if message["id"] == self._request_id and not self._closing:
            if "image" in message:
                image = QImage.fromData(base64.b64decode(message["image"]), "PNG")
                if image.isNull():
                    self._report_failure("No se pudo mostrar la acuarela.")
                else:
                    self.image_ready.emit(image, message["seconds"])
            else:
                self._report_failure(message["error"])
        self._dispatch()

    def _report_failure(self, message):
        self.status.emit(message)
        self.failed.emit(message)

    def _read_diagnostics(self):
        self._diagnostics = (self._diagnostics + bytes(self._process.readAllStandardError()))[-2048:]

    def _gpu_timed_out(self):
        self._failure_detail = "La GPU superó el tiempo de espera."
        self._ready = False
        self._process.kill()

    def _exited(self, exit_code, exit_status):
        self._gpu_timeout.stop()
        self._read_messages()
        self._ready = False
        interrupted = self._inflight
        self._inflight = None
        if not self._closing and self._backend == "gpu":
            self._backend = "cpu"
            if self._pending is None and interrupted and interrupted["id"] == self._request_id:
                self._pending = interrupted
            self.start("GPU no disponible. Cargando generador en CPU…")
            return
        self._pending = None
        if not self._closing:
            diagnostics = self._diagnostics.decode("utf-8", errors="replace").strip().splitlines()
            detail = self._failure_detail or (diagnostics[-1] if diagnostics else f"Código de salida {exit_code}.")
            self._report_failure(f"Se cerró el generador floral. {detail}")
        self.stopped.emit()

    def _process_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self._failure_detail = self._process.errorString()
            if self._backend == "gpu" and not self._closing:
                # Qt aún está notificando el fallo de arranque; reinicia en el siguiente turno.
                QTimer.singleShot(0, self._fallback_after_start_error)
            else:
                self._exited(-1, QProcess.ExitStatus.CrashExit)

    def _fallback_after_start_error(self):
        if not self.running and self._backend == "gpu":
            self._exited(-1, QProcess.ExitStatus.CrashExit)
