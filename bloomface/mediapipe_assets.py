"""Descarga del bundle oficial. No obtiene imágenes de usuarios."""
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

from bloomface.classifier import MODEL_PATH

MODEL_URLS = (
    "https://huggingface.co/litert-community/MediaPipe-FaceLandmarker/resolve/main/face_landmarker.task",
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
)


def valid_bundle(path):
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            return (archive.testzip() is None and any("blendshape" in n for n in names)
                    and any("landmark" in n for n in names) and any("face_detector" in n for n in names))
    except (OSError, zipfile.BadZipFile):
        return False


def ensure_model(path=MODEL_PATH, check_only=False):
    path = Path(path)
    if valid_bundle(path):
        return path
    if check_only:
        raise FileNotFoundError(f"Falta un bundle MediaPipe válido: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".download")
    errors = []
    for url in MODEL_URLS:
        try:
            print("Descargando el modelo facial preentrenado de MediaPipe...", flush=True)
            request = urllib.request.Request(url, headers={"User-Agent": "BloomFace/1.0"})
            with urllib.request.urlopen(request, timeout=30) as response, temporary.open("wb") as target:
                size = 0
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > 100 * 1024 * 1024:
                        raise ValueError("El archivo del modelo supera el tamaño esperado.")
                    target.write(chunk)
            if not valid_bundle(temporary):
                raise ValueError("La descarga no contiene un Face Landmarker con blendshapes.")
            temporary.replace(path)
            path.with_suffix(".json").write_text(json.dumps({"url": url,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}, indent=2), encoding="utf-8")
            return path
        except (OSError, ValueError) as error:
            errors.append(str(error))
            temporary.unlink(missing_ok=True)
    raise RuntimeError("No se pudo descargar MediaPipe. Revisa la conexión. " + " | ".join(errors))
