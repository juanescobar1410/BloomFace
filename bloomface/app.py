from PySide6.QtCore import QElapsedTimer, Qt, QTimer, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from bloomface.camera import CameraThread
from bloomface.composition import FlowerComposition


TRANSITION_DURATION_MS = 1200
ENLARGED_FLOWER_SCALE = 1.15


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

        self._aperture = 0.5
        self._scale = 1.0
        self._transition_from = (self._aperture, self._scale)
        self._transition_target = self._transition_from
        self._transition_clock = QElapsedTimer()
        self._transition = QTimer(self)
        self._transition.setInterval(33)
        self._transition.timeout.connect(self._advance_transition)

        self._flower_view = QLabel()
        self._flower_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flower_view.setWordWrap(True)
        self._flower_view.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self._flower_view.setMinimumSize(320, 240)

        self._simulate_smile = QPushButton("Simular sonrisa")
        self._simulate_smile.clicked.connect(lambda: self._transition_to(1.0))
        self._simulate_rest = QPushButton("Simular reposo")
        self._simulate_rest.clicked.connect(lambda: self._transition_to(0.5))
        self._simulate_frown = QPushButton("Simular ceño fruncido")
        self._simulate_frown.clicked.connect(lambda: self._transition_to(0.0))
        self._simulate_mouth_open = QPushButton("Simular boca abierta")
        self._simulate_mouth_open.clicked.connect(
            lambda: self._transition_to(self._aperture, ENLARGED_FLOWER_SCALE)
        )
        self._gesture_buttons = (
            self._simulate_smile,
            self._simulate_rest,
            self._simulate_frown,
            self._simulate_mouth_open,
        )

        self._pause = QPushButton("Pausar")
        self._pause.clicked.connect(self._toggle_pause)

        controls = QGridLayout()
        for index, button in enumerate(self._gesture_buttons):
            row, column = divmod(index, 2)
            controls.addWidget(button, row, column)
        controls.addWidget(self._pause, 2, 0, 1, 2)

        composition_panel = QVBoxLayout()
        composition_panel.addWidget(QLabel("Tu composición"))
        composition_panel.addWidget(self._flower_view, 1)
        composition_panel.addLayout(controls)

        layout = QHBoxLayout(self)
        layout.addLayout(camera_panel, 1)
        layout.addLayout(composition_panel, 2)

        try:
            self._flower = FlowerComposition()
        except (OSError, ValueError) as error:
            self._flower_view.setText(str(error))
            for button in self._gesture_buttons:
                button.setEnabled(False)
            self._pause.setEnabled(False)
        else:
            self._draw_flower()

    def _draw_flower(self):
        _display_image(self._flower_view, self._flower.render(self._aperture, self._scale))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._flower is not None:
            self._draw_flower()

    def _transition_to(self, aperture, scale=1.0):
        target = (aperture, scale)
        if self._transition.isActive() and target == self._transition_target:
            return
        self._transition_target = target
        self._transition_from = (self._aperture, self._scale)
        if self._transition_from == target:
            self._transition.stop()
            return
        self._transition_clock.start()
        self._transition.start()

    @Slot()
    def _advance_transition(self):
        progress = self._transition_clock.elapsed() / TRANSITION_DURATION_MS
        if progress >= 1.0:
            self._aperture, self._scale = self._transition_target
            self._transition.stop()
        else:
            initial_aperture, initial_scale = self._transition_from
            target_aperture, target_scale = self._transition_target
            self._aperture = initial_aperture + (target_aperture - initial_aperture) * progress
            self._scale = initial_scale + (target_scale - initial_scale) * progress
        self._draw_flower()

    @Slot()
    def _toggle_pause(self):
        self._paused = not self._paused
        self._pause.setText("Reanudar" if self._paused else "Pausar")
        for button in self._gesture_buttons:
            button.setEnabled(not self._paused)
        self._open_camera.setEnabled(not self._paused and self._camera is None)

        if self._paused:
            self._transition.stop()
            self._refresh.stop()
        elif self._camera is not None:
            self._refresh.start()

    @Slot()
    def _start_camera(self):
        self._preview.setText("Abriendo cámara…")
        self._open_camera.setEnabled(False)
        self._camera = CameraThread(self)
        self._camera.finished.connect(self._camera_finished)
        self._camera.start()
        self._refresh.start()

    @Slot()
    def _show_latest_frame(self):
        frame = self._camera.take_frame()
        if frame is not None:
            _display_image(self._preview, frame)

    @Slot()
    def _camera_finished(self):
        self._refresh.stop()
        self._transition.stop()
        camera = self._camera
        self._camera = None
        error = camera.error
        camera.deleteLater()
        if self._closing:
            self.close()
            return
        self._preview.setText(error or "La cámara se cerró.")
        self._open_camera.setText("Reintentar")
        self._open_camera.setEnabled(not self._paused)

    def closeEvent(self, event):
        self._transition.stop()
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
