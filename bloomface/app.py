from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QPixmap
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
from bloomface.composition import FlowerComposition


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
        self._flower = None
        self.setWindowTitle("BloomFace")
        self.resize(850, 480)

        self._camera = None
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

        camera_panel = QVBoxLayout()
        camera_panel.addWidget(QLabel("Vista de cámara"))
        camera_panel.addWidget(self._preview, 1)
        camera_panel.addWidget(self._open_camera)

        self._flower_view = QLabel()
        self._flower_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flower_view.setWordWrap(True)
        self._flower_view.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self._flower_view.setMinimumSize(320, 240)

        self._pause = QPushButton("Pausar")
        self._pause.clicked.connect(self._toggle_pause)

        composition_panel = QVBoxLayout()
        composition_panel.addWidget(QLabel("Tu composición"))
        composition_panel.addWidget(self._flower_view, 1)
        composition_panel.addWidget(self._pause)

        layout = QHBoxLayout(self)
        layout.addLayout(camera_panel, 1)
        layout.addLayout(composition_panel, 2)

        try:
            self._flower = FlowerComposition()
        except (OSError, ValueError) as error:
            self._flower_view.setText(str(error))
            self._pause.setEnabled(False)
        else:
            self._draw_flower()
        self._update_controls()

    def _update_controls(self):
        self._open_camera.setEnabled(not self._paused and self._camera is None)

    def _draw_flower(self):
        _display_image(self._flower_view, self._flower.render())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._flower is not None:
            self._draw_flower()

    @Slot()
    def _toggle_pause(self):
        self._paused = not self._paused
        self._pause.setText("Reanudar" if self._paused else "Pausar")
        if self._paused:
            self._refresh.stop()
        elif self._camera is not None:
            self._refresh.start()
        self._update_controls()

    @Slot()
    def _start_camera(self):
        self._preview.setText("Abriendo cámara…")
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
        if frame is not None:
            _display_image(self._preview, frame)

    @Slot()
    def _camera_finished(self):
        self._refresh.stop()
        camera = self._camera
        self._camera = None
        error = camera.error
        camera.wait()
        camera.deleteLater()
        if self._closing:
            self.close()
            return
        self._preview.setText(error or "La cámara se cerró.")
        self._open_camera.setText("Reintentar")
        self._update_controls()

    def closeEvent(self, event):
        if self._camera is not None:
            self._closing = True
            self._refresh.stop()
            self._camera.requestInterruption()
            event.ignore()
            return
        super().closeEvent(event)


def main():
    app = QApplication([])
    window = BloomFaceWindow()
    window.show()
    return app.exec()
