import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from torch import nn
from torch.nn import functional as F


MODEL_DIR = Path(__file__).resolve().parent / "models"
PROJECT_MODEL_DIR = MODEL_DIR.parents[1] / "models"
CLASSES = ("reposo", "sonrisa", "boca_abierta", "ceno_fruncido")


class GestureCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 6, kernel_size=5, padding=2)
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(16 * 14 * 14, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 4)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.flatten(start_dim=1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


class GestureClassifier:
    def __init__(self, model_dir: Path | None = None):
        if model_dir is None:
            model_dir = MODEL_DIR
            if not model_dir.is_dir() and PROJECT_MODEL_DIR.is_dir():
                model_dir = PROJECT_MODEL_DIR

        config_path = model_dir / "preprocesamiento.json"
        haar_path = model_dir / "haarcascade_frontalface_default.xml"
        weights_path = model_dir / "gestos_parcial2.pt"
        missing = [path.name for path in (config_path, haar_path, weights_path) if not path.is_file()]
        if missing:
            raise FileNotFoundError(f"Archivos faltantes en {model_dir}: {', '.join(missing)}.")

        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        if not isinstance(config, dict) or config.get("clases") != list(CLASSES):
            raise ValueError("El orden de clases en preprocesamiento.json no coincide con el Parcial 2.")
        self.classes = CLASSES
        self.mean = np.asarray(config.get("media"), dtype=np.float64)
        self.scale = np.asarray(config.get("escala"), dtype=np.float64)
        if (
            self.mean.shape != (4096,)
            or self.scale.shape != (4096,)
            or not np.isfinite(self.mean).all()
            or not np.isfinite(self.scale).all()
            or np.any(self.scale <= 0)
        ):
            raise ValueError("El scaler debe incluir 4096 medias finitas y 4096 escalas positivas.")
        self.detector = cv2.CascadeClassifier(str(haar_path))
        if self.detector.empty():
            raise ValueError(f"No se pudo cargar el detector facial: {haar_path}")

        self.model = GestureCNN()
        weights = torch.load(
            weights_path,
            map_location="cpu",
            weights_only=True,
        )
        self.model.load_state_dict(weights)
        self.model.eval()

    def _crop_face(self, image: Image.Image) -> tuple[Image.Image, bool]:
        width, height = image.size
        gray = cv2.equalizeHist(np.asarray(image.convert("L")))

        faces = self.detector.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        if len(faces) == 0:
            faces = self.detector.detectMultiScale(
                gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20)
            )

        detected = len(faces) > 0
        if detected:
            x, y, w, h = map(int, max(faces, key=lambda box: box[2] * box[3]))
            side = min(int(max(w, h) * 1.3), width, height)
            left = max(0, min(x + w // 2 - side // 2, width - side))
            top = max(0, min(y + h // 2 - side // 2, height - side))
        else:
            side = max(1, int(min(width, height) * 0.65))
            left = (width - side) // 2
            top = (height - side) // 2

        return image.crop((left, top, left + side, top + side)), detected

    @torch.inference_mode()
    def predict(self, image: Image.Image) -> tuple[str, list[float], bool]:
        crop, detected = self._crop_face(image.convert("RGB"))
        gray = crop.convert("L").resize((64, 64), Image.Resampling.BILINEAR)
        pixels = np.array(gray, dtype=np.float32).reshape(-1)
        pixels /= 255.0
        pixels -= self.mean
        pixels /= self.scale

        tensor = torch.from_numpy(pixels.reshape(1, 1, 64, 64))
        scores = self.model(tensor).softmax(dim=1)[0]
        return self.classes[int(scores.argmax())], scores.tolist(), detected


def main():
    parser = argparse.ArgumentParser(description="Prueba local de la CNN de BloomFace")
    parser.add_argument("photo", type=Path)
    args = parser.parse_args()

    if not args.photo.is_file():
        parser.error(f"No se encontró la foto: {args.photo}")

    try:
        classifier = GestureClassifier()
        with Image.open(args.photo) as image:
            gesture, scores, detected = classifier.predict(image)
    except (OSError, TypeError, ValueError, RuntimeError, cv2.error) as error:
        parser.exit(1, f"Error de clasificación: {error}\n")

    print(f"Gesto predicho: {gesture}")
    print(f"Recorte: {'rostro detectado' if detected else 'recorte central'}")
    for name, score in zip(classifier.classes, scores):
        print(f"{name}: {score:.4f}")


if __name__ == "__main__":
    main()