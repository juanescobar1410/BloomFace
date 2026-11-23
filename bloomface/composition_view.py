"""Recuadro de composición e indicador de la primera acuarela."""

from math import atan2, pi, sin, tau

import cv2
import numpy as np
from PySide6.QtCore import QElapsedTimer, QPointF, QRectF, QTimer
from PySide6.QtGui import QColor, QImage, QLinearGradient, QPainter, QPainterPath
from PySide6.QtWidgets import QLabel


PLACEHOLDER = "La flor aparecerá aquí."
PETAL_STEP_MS = 230
PETAL_PULSE_MS = 560
SHIMMER_MS = 3500
SYMBOL_SIZE = 52


def _logo_petals(logo_path):
    """Extrae los pétalos del símbolo situado a la derecha del texto de marca."""
    logo = QImage(str(logo_path)).convertToFormat(QImage.Format.Format_RGBA8888)
    if logo.isNull():
        return []
    pixels = np.frombuffer(logo.constBits(), dtype=np.uint8).reshape(logo.height(), logo.width(), 4)
    alpha = pixels[:, :, 3]
    columns = np.flatnonzero(alpha.any(axis=0))
    if not columns.size:
        return []
    gaps = np.flatnonzero(np.diff(columns) > 1)
    start = int(columns[gaps[-1] + 1] if gaps.size else columns[0])
    alpha = alpha[:, start:int(columns[-1]) + 1]
    mask = np.ascontiguousarray(alpha > 0, dtype=np.uint8)
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if count != 9:
        return []

    left, top, width, height = cv2.boundingRect(mask)
    center_x, center_y = left + width / 2, top + height / 2
    size_ratio = SYMBOL_SIZE / max(width, height)
    order = sorted(range(1, count),
                   key=lambda i: atan2(centroids[i, 0] - center_x, center_y - centroids[i, 1]) % tau)
    petals = []
    for index in order:
        x, y, w, h, _ = (int(value) for value in stats[index])
        component = labels[y:y + h, x:x + w] == index
        rgba = np.empty((h, w, 4), dtype=np.uint8)
        rgba[:, :, :3] = (178, 181, 173)
        rgba[:, :, 3] = np.where(component, alpha[y:y + h, x:x + w], 0)
        image = QImage(rgba.data, w, h, rgba.strides[0], QImage.Format.Format_RGBA8888).copy()

        rows, cols = np.nonzero(component)
        base = np.argmin((cols + x + 0.5 - center_x) ** 2 + (rows + y + 0.5 - center_y) ** 2)
        pivot = QPointF((x + cols[base] + 0.5 - center_x) * size_ratio,
                        (y + rows[base] + 0.5 - center_y) * size_ratio)
        bounds = QRectF((x - center_x) * size_ratio, (y - center_y) * size_ratio,
                        w * size_ratio, h * size_ratio)
        petals.append((image, bounds.translated(-pivot), pivot))
    return petals


class CompositionView(QLabel):
    def __init__(self, logo_path):
        super().__init__(PLACEHOLDER)
        self._logo_path = logo_path
        self._petals = None
        self._clock = QElapsedTimer()
        self._animation = QTimer(self)
        self._animation.setInterval(16)
        self._animation.timeout.connect(self.update)

    @property
    def loading(self):
        return self._animation.isActive()

    def set_loading(self, loading):
        if loading == self.loading:
            return
        if loading:
            if self._petals is None:
                self._petals = _logo_petals(self._logo_path)
            self.setText("")
            self.setAccessibleDescription("Generando la primera acuarela.")
            self._clock.start()
            self._animation.start()
        else:
            self._animation.stop()
            self.setAccessibleDescription("")
            if self.pixmap().isNull():
                self.setText(PLACEHOLDER)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.loading:
            return

        elapsed_ms = self._clock.elapsed()
        center = QRectF(self.rect()).center()
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)

        for index, (image, bounds, pivot) in enumerate(self._petals):
            phase = (elapsed_ms - index * PETAL_STEP_MS) % (8 * PETAL_STEP_MS)
            pulse = sin(pi * min(1.0, phase / PETAL_PULSE_MS)) ** 2
            scale = 0.91 + 0.18 * pulse
            painter.save()
            painter.translate(center + pivot)
            painter.scale(scale, scale)
            painter.drawImage(bounds, image)
            painter.restore()

        text = QPainterPath()
        text.addText(0, 0, self.font(), PLACEHOLDER)
        bounds = text.boundingRect()
        text.translate(center.x() - bounds.center().x(), center.y() + 43 - bounds.top())
        bounds = text.boundingRect()
        painter.fillPath(text, QColor("#777969"))
        reach = 23.0
        glint_x = bounds.left() - reach + (bounds.width() + 2 * reach) * (elapsed_ms % SHIMMER_MS) / SHIMMER_MS
        glint = QLinearGradient(glint_x - reach, 0, glint_x + reach, 0)
        glint.setColorAt(0, QColor(250, 249, 244, 0))
        glint.setColorAt(0.5, QColor(250, 249, 244, 65))
        glint.setColorAt(1, QColor(250, 249, 244, 0))
        painter.fillPath(text, glint)
        painter.end()
