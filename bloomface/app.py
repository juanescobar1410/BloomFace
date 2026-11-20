from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from bloomface.camera import CameraThread
from bloomface.floral import FloralProcess
from bloomface.recognition import NO_FACE, WAITING_FOR_GESTURE, RecognitionThread


GESTURES = {
    "reposo": "Reposo",
    "sonrisa": "Sonrisa",
    "boca_abierta": "Boca abierta",
    "ceno_fruncido": "Ceño fruncido",
}


def _display_image(label, image):
    pixmap = QPixmap.fromImage(image).scaled(
        label.size(),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    label.setPixmap(pixmap)


class BloomFaceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BloomFace")
        self.resize(850, 480)

        self._camera = None
        self._camera_has_frame = False
        self._recognition = None
        self._closing = False
        self._paused = False
        self._refresh = QTimer(self)
        self._refresh.setInterval(33)
        self._refresh.timeout.connect(self._show_latest_frame)

        self._preview = QLabel("Abre la cámara para ver el encuadre.")
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setWordWrap(True)
        self._preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self._preview.setMinimumSize(320, 240)

        self._open_camera = QPushButton("Abrir cámara")
        self._open_camera.clicked.connect(self._start_camera)
        self._start_recognition_button = QPushButton("Iniciar reconocimiento")
        self._start_recognition_button.clicked.connect(self._start_recognition)
        self._recognition_status = QLabel()
        self._recognition_status.setWordWrap(True)

        camera_panel = QVBoxLayout()
        camera_panel.addWidget(QLabel("Vista de cámara"))
        camera_panel.addWidget(self._preview, 1)
        camera_panel.addWidget(self._recognition_status)
        camera_panel.addWidget(self._open_camera)
        camera_panel.addWidget(self._start_recognition_button)

        self._generated = None

        self._flower_view = QLabel("La acuarela aparecerá cuando se confirme un gesto.")
        self._flower_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flower_view.setWordWrap(True)
        self._flower_view.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self._flower_view.setMinimumSize(320, 240)

        self._floral_status = QLabel()
        self._floral_status.setWordWrap(True)
        self._generator = FloralProcess(self)
        if not self._generator.enabled:
            self._flower_view.setText("Generación local en pausa.")
        self._generator.status.connect(self._show_floral_status)
        self._generator.image_ready.connect(self._show_generated)
        self._generator.stopped.connect(self._finish_close)

        self._pause = QPushButton("Pausar")
        self._pause.clicked.connect(self._toggle_pause)

        composition_panel = QVBoxLayout()
        composition_panel.addWidget(QLabel("Tu composición"))
        composition_panel.addWidget(self._flower_view, 1)
        composition_panel.addWidget(self._floral_status)
        composition_panel.addWidget(self._pause)

        layout = QHBoxLayout(self)
        layout.addLayout(camera_panel, 1)
        layout.addLayout(composition_panel, 2)

        self._update_controls()

    def _update_controls(self):
        can_change_flower = not self._paused and self._recognition is None
        self._open_camera.setEnabled(not self._paused and self._camera is None)
        self._start_recognition_button.setEnabled(can_change_flower and self._camera_has_frame)

    def _draw_flower(self):
        _display_image(self._flower_view, self._generated)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._generated is not None:
            self._draw_flower()

    @Slot(str)
    def _show_floral_status(self, message):
        if not self._paused and not self._closing:
            self._floral_status.setText(message)

    @Slot(QImage, float)
    def _show_generated(self, image, seconds):
        if self._paused or self._closing:
            return
        self._generated = image
        self._draw_flower()
        self._floral_status.setText(f"Nueva acuarela · {seconds:.1f} s")

    @Slot()
    def _toggle_pause(self):
        self._paused = not self._paused
        self._pause.setText("Reanudar" if self._paused else "Pausar")
        if self._paused:
            self._generator.invalidate()
            self._floral_status.clear()
            self._refresh.stop()
            if self._recognition is not None:
                self._recognition.stop()
            self._recognition_status.setText("En pausa.")
        elif self._camera is not None:
            self._camera_has_frame = False
            self._recognition_status.clear()
            self._refresh.start()
        else:
            self._recognition_status.clear()
        self._update_controls()

    @Slot()
    def _start_recognition(self):
        self._generator.start()
        self._recognition_status.setText("Cargando clasificador…")
        self._recognition = RecognitionThread(self)
        self._recognition.update.connect(self._handle_recognition_update)
        self._recognition.finished.connect(self._recognition_finished)
        self._recognition.start()
        self._update_controls()

    @Slot(str)
    def _handle_recognition_update(self, state):
        recognition = self._recognition
        if recognition is None or self.sender() is not recognition or recognition.stopping:
            return
        if state == NO_FACE:
            self._generator.invalidate()
            self._floral_status.clear()
            self._recognition_status.setText("Rostro no detectado. Vuelve al encuadre.")
        elif state == WAITING_FOR_GESTURE:
            self._recognition_status.setText("Mantén el gesto hasta que se confirme.")
        else:
            self._recognition_status.setText(f"Gesto confirmado: {GESTURES[state]}")
            self._generator.request(state)

    @Slot()
    def _recognition_finished(self):
        recognition = self._recognition
        self._recognition = None
        error = recognition.error
        recognition.wait()
        recognition.deleteLater()
        if self._closing:
            self._finish_close()
            return
        if error and self._camera_has_frame and not self._paused:
            self._generator.invalidate()
            self._floral_status.clear()
            self._recognition_status.setText(f"No se pudo usar el clasificador. {error}")
        self._update_controls()

    @Slot()
    def _start_camera(self):
        self._preview.setText("Abriendo cámara…")
        self._camera_has_frame = False
        self._camera = CameraThread(self)
        self._camera.finished.connect(self._camera_finished)
        self._camera.start()
        self._refresh.start()
        self._update_controls()

    @Slot()
    def _show_latest_frame(self):
        if self._camera is None:
            return
        frame = self._camera.take_frame()
        if frame is None:
            return
        _display_image(self._preview, frame)
        if not self._camera_has_frame:
            self._camera_has_frame = True
            self._recognition_status.setText("Centra tu rostro e inicia el reconocimiento.")
            self._update_controls()
        if self._recognition is not None:
            self._recognition.submit_frame(frame)

    @Slot()
    def _camera_finished(self):
        self._refresh.stop()
        self._generator.invalidate()
        self._floral_status.clear()
        camera = self._camera
        self._camera = None
        self._camera_has_frame = False
        if self._recognition is not None:
            self._recognition.stop()
        error = camera.error
        camera.wait()
        camera.deleteLater()
        if self._closing:
            self._finish_close()
            return
        self._preview.setText(error or "La cámara se cerró.")
        self._open_camera.setText("Reintentar")
        self._recognition_status.clear()
        self._update_controls()

    def _finish_close(self):
        if self._closing and self._camera is None and self._recognition is None and not self._generator.running:
            self.close()

    def closeEvent(self, event):
        if self._camera is not None or self._recognition is not None or self._generator.running:
            self._closing = True
            self._refresh.stop()
            if self._camera is not None:
                self._camera.requestInterruption()
            if self._recognition is not None:
                self._recognition.stop()
            self._generator.close()
            event.ignore()
            return
        super().closeEvent(event)


def main():
    app = QApplication([])
    window = BloomFaceWindow()
    window.show()
    return app.exec()
