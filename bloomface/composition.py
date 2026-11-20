from math import isfinite
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter


FLOWERS_DIR = Path(__file__).resolve().parent / "assets" / "flowers"


def _load_flower(path: Path) -> QImage:
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró la imagen {path.name}.")

    source = QImage(str(path))
    if source.isNull():
        raise ValueError(f"No se pudo leer la imagen {path.name}.")

    image = QImage(source.size(), QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.white)
    painter = QPainter(image)
    try:
        painter.drawImage(0, 0, source)
    finally:
        painter.end()
    return image


class FlowerComposition:
    def __init__(self):
        self._closed = _load_flower(FLOWERS_DIR / "closed.png")
        self._open = _load_flower(FLOWERS_DIR / "open.png")
        if self._closed.size() != self._open.size():
            raise ValueError("closed.png y open.png deben tener el mismo tamaño.")

    def render(self, aperture: float = 0.5, scale: float = 1.0) -> QImage:
        """Dibuja la flor con la apertura y la escala indicadas en un lienzo fijo."""
        if not 0.0 <= aperture <= 1.0:
            raise ValueError("La apertura debe estar entre 0 y 1.")
        if not isfinite(scale) or scale <= 0.0:
            raise ValueError("La escala debe ser positiva y finita.")

        image = self._closed.copy()
        painter = QPainter(image)
        try:
            painter.setOpacity(aperture)
            painter.drawImage(0, 0, self._open)
        finally:
            painter.end()

        if scale == 1.0:
            return image

        scaled = QImage(image.size(), QImage.Format.Format_RGB32)
        scaled.fill(Qt.GlobalColor.white)
        painter = QPainter(scaled)
        try:
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.translate(image.width() / 2, image.height() / 2)
            painter.scale(scale, scale)
            painter.translate(-image.width() / 2, -image.height() / 2)
            painter.drawImage(0, 0, image)
        finally:
            painter.end()
        return scaled
