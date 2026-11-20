import base64
import json
import os
from pathlib import Path
from tempfile import gettempdir

from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, Signal
from PySide6.QtGui import QImage


class FloralProcess(QObject):
    status = Signal(str)
    image_ready = Signal(QImage, float)
    stopped = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._read_messages)
        self._process.readyReadStandardError.connect(self._read_diagnostics)
        self._process.finished.connect(self._exited)
        self._process.errorOccurred.connect(self._process_error)
        self.enabled = os.environ.get("BLOOMFACE_ENABLE_LOCAL_GENERATOR") == "1"
        runtime = os.environ.get("BLOOMFACE_FLORAL_RUNTIME")
        self._root = Path(runtime).expanduser() if runtime else Path(gettempdir()) / "BloomFace-floral-directml"
        self._notebook = (
            Path(__file__).resolve().parents[1] / "notebooks" / "BloomFace_Generacion_Floral.ipynb"
        )
        self._buffer = bytearray()
        self._diagnostics = b""
        self._ready = False
        self._closing = False
        self._pending = None
        self._inflight = None
        self._request_id = 0

    @property
    def running(self):
        return self._process.state() != QProcess.ProcessState.NotRunning

    def start(self):
        if not self.enabled or self.running or self._closing:
            return
        python = self._root / "venv" / "Scripts" / "python.exe"
        weights = self._root / "weights"
        model_dirs_present = all((weights / name).is_dir() for name in ("sd15", "scribble", "lcm"))
        if not python.is_file() or not model_dirs_present or not self._notebook.is_file():
            self.status.emit("No se encontró el entorno local del generador floral.")
            return
        self._buffer.clear()
        self._diagnostics = b""
        self._ready = False
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert("HF_HUB_OFFLINE", "1")
        environment.insert("TRANSFORMERS_OFFLINE", "1")
        environment.insert("PYTHONUTF8", "1")
        environment.insert("PYTHONDONTWRITEBYTECODE", "1")
        self._process.setProcessEnvironment(environment)
        worker = Path(__file__).with_name("floral_worker.py")
        self.status.emit("Cargando generador floral…")
        self._process.start(str(python), [str(worker), str(self._notebook), str(weights)])

    def request(self, gesture):
        if not self.enabled:
            return
        self._request_id += 1
        self._pending = {"id": self._request_id, "gesture": gesture}
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
        if not self._ready or self._inflight is not None or self._pending is None:
            return
        self._inflight = self._pending["id"]
        payload = json.dumps(self._pending).encode("utf-8") + b"\n"
        self._pending = None
        self.status.emit("Generando acuarela…")
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
            if message.get("ready"):
                self._ready = True
                if self._pending is None:
                    self.status.emit("Generador listo.")
                self._dispatch()
            elif "id" not in message:
                if not self._closing:
                    self.status.emit(f"No se pudo cargar el generador. {message['error']}")
            else:
                self._handle_result(message)

    def _handle_result(self, message):
        if message["id"] != self._inflight:
            return
        self._inflight = None
        if message["id"] == self._request_id and not self._closing:
            if "image" in message:
                image = QImage.fromData(base64.b64decode(message["image"]), "PNG")
                if image.isNull():
                    self.status.emit("No se pudo mostrar la acuarela.")
                else:
                    self.image_ready.emit(image, message["seconds"])
            else:
                self.status.emit(message["error"])
        self._dispatch()

    def _read_diagnostics(self):
        self._diagnostics = (self._diagnostics + bytes(self._process.readAllStandardError()))[-2048:]

    def _exited(self, exit_code, exit_status):
        self._ready = False
        self._inflight = None
        self._pending = None
        if exit_code and not self._closing:
            diagnostic = self._diagnostics.decode("utf-8", errors="replace").strip().splitlines()
            detail = diagnostic[-1] if diagnostic else f"Código de salida {exit_code}."
            self.status.emit(f"Se cerró el generador floral. {detail}")
        self.stopped.emit()

    def _process_error(self, error):
        if error == QProcess.ProcessError.FailedToStart and not self._closing:
            self.status.emit(f"No se pudo iniciar el generador. {self._process.errorString()}")
