from html import escape
from pathlib import Path
import sys

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QColor, QFont, QFontDatabase, QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from bloomface.camera import CameraThread
from bloomface.classifier import NEUTRAL_PATH
from bloomface.floral import FloralProcess
from bloomface.recognition import NO_FACE, WAITING_FOR_GESTURE, RecognitionThread


PROJECT_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
LOGO_PATH = PROJECT_ROOT / "bloomface" / "assets" / "brand" / "BloomFace_Logo.png"
FONT_DIR = PROJECT_ROOT / "agrandir-font-family"
_FONT_IDS = []

GESTURES = {
    "reposo": "Reposo",
    "sonrisa": "Sonrisa",
    "boca_abierta": "Boca abierta",
    "ceno_fruncido": "Ceño fruncido",
}


APP_STYLE = """
QWidget {
    color: #20221b;
    font-family: "Agrandir";
    font-size: 14px;
}
QStackedWidget, QWidget#page { background-color: #f8f8f2; }
QLabel#muted { color: #666f50; }
QLabel#pageTitle { color: #26271f; font-size: 28px; }
QLabel#sectionTitle { color: #60694b; font-size: 15px; }
QLabel#cameraView {
    background-color: #dedfce;
    border: 0;
    border-radius: 8px;
    color: #60694b;
    padding: 8px;
}
QLabel#compositionView {
    background-color: #faf9f4;
    border: 1px solid #25251f;
    border-radius: 6px;
    color: #777969;
    padding: 8px;
}
QLabel#statusPill {
    background: transparent;
    border: 2px solid #60694b;
    border-radius: 24px;
    color: #60694b;
    font-size: 13px;
    padding: 8px 22px;
}
QLabel#cameraError {
    background-color: #ffebed;
    border: 1px solid #aa1760;
    border-radius: 12px;
    color: #a21f64;
    padding: 10px 14px;
}
QPushButton {
    background-color: #60694b;
    border: 0;
    border-radius: 6px;
    color: white;
    font-weight: 700;
    min-height: 44px;
    padding: 0 30px;
}
QPushButton:hover { background-color: #515b3e; }
QPushButton:disabled { background-color: #d5d6c7; color: #858775; }
QPushButton#primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #96336f, stop:1 #d27579);
    color: white;
}
QPushButton#primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #84265f, stop:1 #c0646e);
}
QPushButton#secondary { background-color: #60694b; color: white; }
QPushButton#outline {
    background: transparent;
    border: 2px solid #60694b;
    border-radius: 24px;
    color: #60694b;
    font-weight: 400;
}
QPushButton#outline:hover { background-color: #ececdf; }
QPushButton#linkButton {
    background-color: #60694b;
    border: 0;
    border-radius: 8px;
    color: white;
    font-size: 12px;
    font-weight: 700;
    min-height: 38px;
    padding: 0 14px;
}
QPushButton#linkButton:hover { background-color: #515b3e; }
"""


def _load_agrandir():
    family = None
    for filename in ("Agrandir-Regular.otf", "Agrandir-TextBold.otf"):
        path = FONT_DIR / filename
        if path.is_file():
            font_id = QFontDatabase.addApplicationFont(str(path))
            if font_id >= 0:
                _FONT_IDS.append(font_id)
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families and family is None:
                    family = families[0]
    return family
def _logo_label(width):
    label = QLabel()
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    source = QPixmap(str(LOGO_PATH))
    if source.isNull():
        label.setText("BLOOM FACE")
        return label
    pixmap = source.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
    label.setPixmap(pixmap)
    label.setFixedSize(pixmap.size())
    return label
def _display_image(label, image):
    pixmap = QPixmap.fromImage(image).scaled(
        label.size(), Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    label.setPixmap(pixmap)


def _shadow(widget):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(18)
    effect.setOffset(0, 7)
    effect.setColor(QColor("#787568"))
    widget.setGraphicsEffect(effect)


class BloomFaceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BloomFace")
        self.resize(1224, 688)
        self.setMinimumSize(900, 540)
        self.setStyleSheet(APP_STYLE)

        self._camera = None
        self._camera_has_frame = False
        self._recognition = None
        self._closing = False
        self._paused = False
        self._neutral_calibrating = False
        self._return_to_instructions = False
        self._resume_after_stop = False
        self._error_retry = None
        self._banner_kind = None
        self._no_face_samples = 0
        self._face_samples = 0
        self._generated = None
        self._refresh = QTimer(self)
        self._refresh.setInterval(33)
        self._refresh.timeout.connect(self._show_latest_frame)

        self._generator = FloralProcess(self)
        self._generator.status.connect(self._show_floral_status)
        self._generator.image_ready.connect(self._show_generated)
        self._generator.stopped.connect(self._finish_close)

        self._screens = QStackedWidget(self)
        self._welcome_page = self._build_welcome_page()
        self._instructions_page = self._build_instructions_page()
        self._main_page = self._build_main_page()
        for page in (self._welcome_page, self._instructions_page, self._main_page):
            self._screens.addWidget(page)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._screens)
        self._screens.setCurrentWidget(self._welcome_page)

    def _build_welcome_page(self):
        page = QWidget()
        page.setObjectName("page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(36, 30, 36, 32)
        layout.addStretch(1)
        logo = _logo_label(690)
        subtitle = QLabel("Transforma una composición floral mediante gestos visibles\nde tu rostro")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size:22px; color:#181914;")
        start = QPushButton("INICIAR")
        start.setObjectName("secondary")
        start.setMinimumSize(374, 106)
        start.clicked.connect(lambda: self._screens.setCurrentWidget(self._instructions_page))
        _shadow(start)
        _shadow(start)
        layout.addWidget(logo, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(18)
        layout.addWidget(subtitle)
        layout.addSpacing(56)
        layout.addWidget(start, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)
        return page

    def _build_instructions_page(self):
        page = QWidget()
        page.setObjectName("page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(64, 40, 64, 34)
        instruction = QLabel("Ubícate de frente en tu dispositivo · incluye cejas y boca en la imagen · luz estable")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setStyleSheet("font-size:22px;")

        camera_mock = QLabel("Ubícate dentro del encuadre\n\nAsegúrate de que se vean tus cejas y tu boca")
        camera_mock.setObjectName("cameraView")
        camera_mock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        camera_mock.setWordWrap(True)
        camera_mock.setMinimumSize(560, 340)
        camera_mock.setMaximumWidth(760)
        camera_mock.setStyleSheet("font-size:20px; border:3px solid white; border-radius:20px; padding:28px;")

        arrow = QPushButton("→")
        arrow.setObjectName("outline")
        arrow.setFixedSize(96, 62)
        arrow.setStyleSheet("font-size:30px; font-weight:400;")
        arrow.clicked.connect(self._enter_main)
        footer = QHBoxLayout()
        back = QPushButton("Volver")
        back.setObjectName("linkButton")
        back.clicked.connect(lambda: self._screens.setCurrentWidget(self._welcome_page))
        footer.addWidget(back, 0, Qt.AlignmentFlag.AlignLeft)
        footer.addStretch(1)
        footer.addWidget(arrow, 0, Qt.AlignmentFlag.AlignRight)

        layout.addWidget(instruction)
        layout.addStretch(1)
        layout.addWidget(camera_mock, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)
        layout.addLayout(footer)
        return page

    def _build_main_page(self):
        page = QWidget()
        page.setObjectName("page")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(34, 14, 34, 16)
        outer.setSpacing(10)

        header = QHBoxLayout()
        header.addWidget(_logo_label(230), 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.addStretch(1)
        self._state_pill = QLabel("Vista Previa")
        self._state_pill.setObjectName("statusPill")
        self._state_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._state_pill.setMinimumWidth(220)
        self._state_pill.setFixedHeight(50)
        header.addWidget(self._state_pill, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        outer.addLayout(header)

        titles = QHBoxLayout()
        camera_title = QLabel("Vista de cámara")
        camera_title.setObjectName("muted")
        composition_title = QLabel("Tu composición")
        composition_title.setObjectName("muted")
        titles.addWidget(camera_title, 1)
        titles.addSpacing(22)
        titles.addWidget(composition_title, 1)
        outer.addLayout(titles)

        panels = QHBoxLayout()
        panels.setSpacing(26)
        self._preview = QLabel("Abriendo cámara…")
        self._preview.setObjectName("cameraView")
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setWordWrap(True)
        self._preview.setMinimumSize(320, 260)
        self._preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)

        self._flower_view = QLabel("La flor aparecerá aquí.")
        self._flower_view.setObjectName("compositionView")
        self._flower_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flower_view.setWordWrap(True)
        self._flower_view.setMinimumSize(360, 260)
        self._flower_view.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)

        camera_column = QVBoxLayout()
        camera_column.setSpacing(8)
        camera_column.addWidget(self._preview, 1)
        self._camera_error_banner = QLabel()
        self._camera_error_banner.setObjectName("cameraError")
        self._camera_error_banner.setWordWrap(True)
        self._camera_error_banner.hide()
        camera_column.addWidget(self._camera_error_banner)
        self._adjust_neutral = QPushButton("Ajustar reposo")
        self._adjust_neutral.setObjectName("linkButton")
        self._adjust_neutral.clicked.connect(self._calibrate_neutral)
        self._reset_neutral = QPushButton("Restablecer referencia")
        self._reset_neutral.setObjectName("linkButton")
        self._reset_neutral.clicked.connect(self._restore_neutral)
        calibrate_row = QHBoxLayout()
        calibrate_row.addWidget(self._adjust_neutral)
        calibrate_row.addWidget(self._reset_neutral)
        camera_column.addLayout(calibrate_row)

        composition_column = QVBoxLayout()
        composition_column.setSpacing(0)
        composition_column.addWidget(self._flower_view, 1)
        panels.addLayout(camera_column, 1)
        panels.addLayout(composition_column, 1.12)
        outer.addLayout(panels, 1)

        self._status_message = QLabel("Ajusta el encuadre antes de iniciar")
        self._status_message.setObjectName("muted")
        self._status_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_message.setMinimumHeight(28)
        outer.addWidget(self._status_message)

        self._actions = QStackedWidget()
        self._actions.addWidget(self._build_preview_actions())
        self._actions.addWidget(self._build_active_actions())
        self._actions.addWidget(self._build_paused_actions())
        self._actions.addWidget(self._build_error_actions())
        self._actions.setCurrentIndex(0)
        outer.addWidget(self._actions)
        return page

    def _action_row(self):
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)
        return row, layout

    def _build_preview_actions(self):
        row, layout = self._action_row()
        self._start_recognition_button = QPushButton("Iniciar")
        self._start_recognition_button.setObjectName("primary")
        self._start_recognition_button.setMinimumWidth(176)
        self._start_recognition_button.clicked.connect(self._start_recognition)
        back = QPushButton("Volver")
        back.setObjectName("secondary")
        back.setMinimumWidth(176)
        back.clicked.connect(self._back_to_instructions)
        layout.addWidget(self._start_recognition_button)
        layout.addSpacing(18)
        layout.addWidget(back)
        layout.addStretch(1)
        return row

    def _build_active_actions(self):
        row, layout = self._action_row()
        self._pause = QPushButton("Pausar")
        self._pause.setObjectName("primary")
        self._pause.setMinimumWidth(176)
        self._pause.clicked.connect(self._toggle_pause)
        layout.addWidget(self._pause)
        layout.addStretch(1)
        return row

    def _build_paused_actions(self):
        row, layout = self._action_row()
        resume = QPushButton("Reanudar")
        resume.setObjectName("primary")
        resume.setMinimumWidth(176)
        resume.clicked.connect(self._toggle_pause)
        finish = QPushButton("Finalizar")
        finish.setObjectName("secondary")
        finish.setMinimumWidth(176)
        finish.clicked.connect(self.close)
        layout.addWidget(resume)
        layout.addSpacing(18)
        layout.addWidget(finish)
        layout.addStretch(1)
        return row

    def _build_error_actions(self):
        row, layout = self._action_row()
        self._retry_button = QPushButton("Reintentar")
        self._retry_button.setObjectName("primary")
        self._retry_button.setMinimumWidth(176)
        self._retry_button.clicked.connect(self._retry_error)
        finish = QPushButton("Finalizar")
        finish.setObjectName("secondary")
        finish.setMinimumWidth(176)
        finish.clicked.connect(self.close)
        layout.addWidget(self._retry_button)
        layout.addSpacing(18)
        layout.addWidget(finish)
        layout.addStretch(1)
        return row

    def _enter_main(self):
        self._screens.setCurrentWidget(self._main_page)
        self._paused = False
        self._set_view_state("preview")
        self._start_camera()

    def _back_to_instructions(self):
        if self._camera is None:
            self._screens.setCurrentWidget(self._instructions_page)
            return
        self._return_to_instructions = True
        self._refresh.stop()
        self._camera.requestInterruption()

    def _set_view_state(self, state, status_text=None):
        self._view_state = state
        labels = {
            "preview": "Vista Previa",
            "waiting": "Esperando gesto estable",
            "paused": "En pausa",
            "camera_error": "Cámara no disponible",
            "recognition_error": "Error de reconocimiento",
        }
        self._state_pill.setText(labels.get(state, state))
        if status_text is not None:
            self._status_message.setText(status_text)
        action_indices = {
            "preview": 0, "waiting": 1, "paused": 2,
            "camera_error": 3, "recognition_error": 3,
        }
        self._actions.setCurrentIndex(action_indices.get(state, 0))

    def _set_error_banner(self, message):
        self._camera_error_banner.setTextFormat(Qt.TextFormat.RichText)
        self._camera_error_banner.setText(f"<b>Error</b><br>{escape(message)}")

    def _show_error(self, message, retry, camera_error=True):
        self._banner_kind = "camera" if camera_error else "recognition"
        self._set_error_banner(message)
        self._camera_error_banner.show()
        self._error_retry = retry
        self._set_view_state(
            "camera_error" if camera_error else "recognition_error",
            "Revisa la conexión y reintenta" if camera_error else "Revisa el mensaje y vuelve a intentarlo",
        )

    @Slot()
    def _retry_error(self):
        retry = self._error_retry
        self._error_retry = None
        self._banner_kind = None
        self._no_face_samples = 0
        self._face_samples = 0
        self._camera_error_banner.clear()
        self._camera_error_banner.hide()
        self._set_view_state("preview", "Ajusta el encuadre antes de iniciar")
        if retry is not None:
            retry()

    def _update_controls(self):
        if not hasattr(self, "_start_recognition_button"):
            return
        self._start_recognition_button.setEnabled(
            not self._paused and not self._closing and self._camera_has_frame
            and self._recognition is None
        )
        self._adjust_neutral.setEnabled(
            not self._paused and not self._closing
            and self._recognition is not None and not self._recognition.stopping
        )
        self._reset_neutral.setEnabled(not self._paused and not self._closing)

    @Slot()
    def _calibrate_neutral(self):
        if self._recognition is None or self._recognition.stopping:
            return
        self._generator.invalidate()
        self._neutral_calibrating = True
        self._recognition.calibrate_neutral()
        self._status_message.setText("Mantén boca y cejas relajadas durante 16 muestras válidas")

    @Slot()
    def _restore_neutral(self):
        if self._recognition is not None:
            self._recognition.stop()
        self._generator.invalidate()
        self._neutral_calibrating = False
        try:
            NEUTRAL_PATH.unlink(missing_ok=True)
            self._status_message.setText("Referencia eliminada. Vuelve a iniciar el reconocimiento")
        except OSError as error:
            self._status_message.setText(f"No se pudo eliminar la referencia: {error}")
        self._update_controls()

    @Slot(object)
    def _show_diagnostic(self, result):
        if (self._paused or self._closing or self._recognition is None
                or self.sender() is not self._recognition or self._recognition.stopping):
            return

        if result.get("face_detected"):
            self._face_samples += 1
            self._no_face_samples = 0
            if self._banner_kind == "no_face" and self._face_samples >= 2:
                self._banner_kind = None
                self._camera_error_banner.clear()
                self._camera_error_banner.hide()
                self._set_view_state("waiting", "Mantén un gesto hasta que la flor responda")
        else:
            self._no_face_samples += 1
            self._face_samples = 0
            if self._no_face_samples >= 3 and self._banner_kind is None:
                self._banner_kind = "no_face"
                self._set_error_banner(
                    "No se detectó ningún rostro. Ubícate frente a la cámara "
                    "y asegúrate de que tu rostro esté bien iluminado."
                )
                self._camera_error_banner.show()
                self._state_pill.setText("Rostro no detectado")
                self._status_message.setText("Ubícate dentro del encuadre")

        self._neutral_calibrating = bool(result.get("calibrating_neutral"))
        if result.get("neutral_message"):
            self._status_message.setText(result["neutral_message"])

    def _draw_flower(self):
        if self._generated is not None:
            _display_image(self._flower_view, self._generated)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._draw_flower()

    @Slot(str)
    def _show_floral_status(self, message):
        if not self._paused and not self._closing and message:
            self._status_message.setText(message)

    @Slot(QImage, float)
    def _show_generated(self, image, seconds):
        if self._paused or self._closing:
            return
        self._generated = image
        self._draw_flower()
        self._status_message.setText(f"Nueva acuarela · {seconds:.1f} s")

    @Slot()
    def _toggle_pause(self):
        if not self._paused:
            self._paused = True
            self._resume_after_stop = False
            self._generator.invalidate()
            self._refresh.stop()
            if self._recognition is not None:
                self._recognition.stop()
            self._set_view_state("paused", "La composición se conserva en pantalla")
            return
        self._paused = False
        self._resume_after_stop = True
        self._set_view_state("waiting", "Mantén un gesto hasta que la flor responda")
        self._refresh.start()
        if self._recognition is None and self._camera_has_frame:
            self._resume_after_stop = False
            self._start_recognition()

    @Slot()
    def _start_recognition(self):
        if self._recognition is not None or not self._camera_has_frame or self._paused:
            return
        self._generator.start()
        self._status_message.setText("Mantén un gesto hasta que la flor responda")
        self._set_view_state("waiting")
        self._recognition = RecognitionThread(self)
        self._recognition.update.connect(self._handle_recognition_update)
        self._recognition.diagnostic.connect(self._show_diagnostic)
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
            self._set_view_state("waiting", "Ubícate dentro del encuadre y mantén un gesto claro")
            if self._banner_kind == "no_face":
                self._state_pill.setText("Rostro no detectado")
        elif state == WAITING_FOR_GESTURE:
            if self._banner_kind == "no_face":
                self._state_pill.setText("Rostro no detectado")
            elif not self._neutral_calibrating:
                self._set_view_state("waiting", "Mantén un gesto hasta que la flor responda")
        else:
            label = GESTURES[state]
            self._set_view_state("waiting", "Cambia de gesto para continuar o pausa para conservar la vista")
            self._state_pill.setText(f"Gesto estable: {label}")
            self._generator.request(state)

    @Slot()
    def _recognition_finished(self):
        recognition = self._recognition
        if recognition is None:
            return
        self._recognition = None
        error = recognition.error
        recognition.wait()
        recognition.deleteLater()
        if self._closing:
            self._finish_close()
            return
        if self._resume_after_stop and not self._paused:
            self._resume_after_stop = False
            self._start_recognition()
        elif error and self._camera_has_frame and not self._paused:
            self._generator.invalidate()
            self._show_error(f"No se pudo iniciar el reconocimiento. {error}", self._start_recognition, camera_error=False)
        self._update_controls()

    @Slot()
    def _start_camera(self):
        if self._camera is not None or self._closing:
            return
        self._banner_kind = None
        self._no_face_samples = 0
        self._face_samples = 0
        self._camera_error_banner.clear()
        self._camera_error_banner.hide()
        self._preview.setText("Abriendo cámara…")
        self._camera_has_frame = False
        self._camera = CameraThread(self)
        self._camera.finished.connect(self._camera_finished)
        self._camera.start()
        self._refresh.start()
        self._update_controls()

    def _show_latest_frame(self):
        if self._camera is None:
            return
        frame = self._camera.take_frame()
        if frame is None:
            return
        _display_image(self._preview, frame)
        if not self._camera_has_frame:
            self._camera_has_frame = True
            if self._view_state == "preview":
                self._status_message.setText("Ajusta el encuadre antes de iniciar")
            self._update_controls()
        if self._recognition is not None:
            self._recognition.submit_frame(frame)

    @Slot()
    def _camera_finished(self):
        self._refresh.stop()
        self._generator.invalidate()
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
        if self._return_to_instructions:
            self._return_to_instructions = False
            self._screens.setCurrentWidget(self._instructions_page)
            return
        if self._paused:
            return
        if error:
            self._preview.setText("Cámara no disponible")
            self._show_error(error, self._start_camera, camera_error=True)
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
    if _load_agrandir():
        app.setFont(QFont("Agrandir"))
    window = BloomFaceWindow()
    window.show()
    return app.exec()