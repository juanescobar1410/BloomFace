"""Vista de cámara con una barra de confirmación sobre el borde."""

from PySide6.QtCore import QEasingCurve, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPen, QTransform
from PySide6.QtWidgets import QLabel


class CameraPreview(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self._progress = 0.0
        self._ease = QEasingCurve(QEasingCurve.Type.InOutCubic)
        self._transition = QVariantAnimation(self)
        self._transition.setDuration(125)
        self._transition.valueChanged.connect(self._set_painted_progress)

    def set_gesture_progress(self, progress):
        self._transition.stop()
        if progress in (0.0, 1.0):
            self._set_painted_progress(progress)
        else:
            self._transition.setStartValue(self._progress)
            self._transition.setEndValue(progress)
            self._transition.start()

    def _set_painted_progress(self, progress):
        self._progress = progress
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._progress <= 0:
            return

        rect = QRectF(self.rect()).adjusted(4.0, 4.0, -4.0, -4.0)
        top, bottom, right = rect.top(), rect.bottom(), rect.right()
        center_x = rect.center().x()
        radius = 7.0
        path = QPainterPath()
        path.moveTo(center_x, bottom)
        path.lineTo(right - radius, bottom)
        path.quadTo(right, bottom, right, bottom - radius)
        path.lineTo(right, top + radius)
        path.quadTo(right, top, right - radius, top)
        path.lineTo(center_x, top)
        mirrored = QTransform(-1, 0, 0, 1, 2 * center_x, 0).map(path)
        length = path.length()
        complete = self._progress == 1.0
        eased = self._ease.valueForProgress(self._progress)
        visible = eased * (length - 9.0)
        ready = QColor("#29c56f")
        blend = min(1.0, max(0.0, (self._progress - 0.82) / 0.18))
        ramp = tuple(
            QColor.fromRgbF(
                start.redF() + (ready.redF() - start.redF()) * blend,
                start.greenF() + (ready.greenF() - start.greenF()) * blend,
                start.blueF() + (ready.blueF() - start.blueF()) * blend,
            )
            for start in (QColor("#96336f"), QColor("#d27579"))
        )

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for width, alpha in ((15.0, 35), (10.0, 65), (6.5, 112), (3.5, 255)):
            gradient = QLinearGradient(rect.topLeft(), rect.topRight())
            for stop, color in enumerate(ramp):
                color.setAlpha(alpha)
                gradient.setColorAt(stop, color)
            pen = QPen(QBrush(gradient), width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                       Qt.PenJoinStyle.RoundJoin)
            if not complete:
                pen.setDashPattern([max(0.01, visible / width), length / width + 1.0])
            painter.setPen(pen)
            painter.drawPath(path)
            painter.drawPath(mirrored)
        painter.end()
