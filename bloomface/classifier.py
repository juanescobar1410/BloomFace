"""Face Landmarker preentrenado + decisión explícita sobre movimientos faciales."""
import json
import math
from pathlib import Path
from time import monotonic, perf_counter

import numpy as np
from PIL import Image

FEATURES = ("mouthSmileLeft", "mouthSmileRight", "jawOpen", "browDownLeft", "browDownRight")
MODEL_DIR = Path(__file__).resolve().parent / "models/mediapipe"
MODEL_PATH = MODEL_DIR / "face_landmarker.task"
NEUTRAL_PATH = MODEL_DIR / "reposo.json"


class BlendshapeDecision:
    """Reglas iniciales, aún no seleccionadas mediante validación del equipo."""
    def __init__(self, neutral=None):
        self.neutral = {name: 0.0 for name in FEATURES}
        if neutral:
            for name in FEATURES:
                value = float(neutral[name])
                if not math.isfinite(value) or not 0 <= value < .95:
                    raise ValueError("La referencia de reposo no es válida; vuelve a ajustarla.")
                self.neutral[name] = value

    def decide(self, raw):
        if any(name not in raw for name in FEATURES):
            raise ValueError("El modelo no devolvió los blendshapes faciales requeridos.")
        adjusted = {}
        for name in FEATURES:
            value = float(raw[name])
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("MediaPipe devolvió una intensidad facial inválida.")
            base = self.neutral[name]
            adjusted[name] = max(0.0, min(1.0, (value - base) / (1 - base)))
        smile = (adjusted["mouthSmileLeft"] + adjusted["mouthSmileRight"]) / 2
        jaw = adjusted["jawOpen"]
        brow = min(adjusted["browDownLeft"], adjusted["browDownRight"])
        strengths = [max(0., 1 - max(smile, jaw, brow)), smile, jaw, brow]
        if smile >= .45 and brow < .35:
            gesture = "sonrisa"  # Sonrisa con boca abierta sigue siendo sonrisa.
        elif jaw >= .45 and smile < .30 and brow < .35:
            gesture = "boca_abierta"
        elif brow >= .35 and smile < .30 and jaw < .30:
            gesture = "ceno_fruncido"
        elif max(smile, jaw, brow) < .20:
            gesture = "reposo"
        else:
            gesture = None  # Mezcla o transición: no fuerza una de las clases.
        return gesture, strengths, adjusted


class GestureClassifier:
    model_label = "MediaPipe Face Landmarker"

    def __init__(self, model_path=MODEL_PATH, neutral_path=NEUTRAL_PATH, running_mode="video"):
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        self._mp = mp
        if running_mode not in ("video", "image"):
            raise ValueError("running_mode debe ser video o image")
        self._video = running_mode == "video"
        self.neutral_path = Path(neutral_path)
        neutral = None
        if self.neutral_path.is_file():
            neutral = json.loads(self.neutral_path.read_text(encoding="utf-8"))["neutral"]
        self.decision = BlendshapeDecision(neutral)
        if not Path(model_path).is_file():
            raise FileNotFoundError(f"Falta el modelo preentrenado de MediaPipe: {model_path}. Ejecuta la preparación del notebook.")
        options = vision.FaceLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(model_path),
                                           delegate=python.BaseOptions.Delegate.CPU),
            running_mode=vision.RunningMode.VIDEO if self._video else vision.RunningMode.IMAGE, num_faces=1,
            output_face_blendshapes=True,
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)
        self._last_timestamp = -1
        self._neutral_samples = None
        self._neutral_target = 16

    def begin_neutral_calibration(self):
        self._neutral_samples = []

    def diagnose(self, image):
        started = perf_counter()
        rgb = image.convert("RGB")
        # El modelo recibe RGB; la miniatura gris es sólo una vista de referencia.
        resized = rgb.copy()
        resized.thumbnail((640, 640), Image.Resampling.BILINEAR)
        mp_image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB,
                                  data=np.ascontiguousarray(np.asarray(resized)))
        timestamp = max(self._last_timestamp + 1, int(monotonic() * 1000))
        self._last_timestamp = timestamp
        result = (self.landmarker.detect_for_video(mp_image, timestamp) if self._video
                  else self.landmarker.detect(mp_image))
        detected = bool(result.face_landmarks and result.face_blendshapes)
        crop = rgb
        raw, adjusted, gesture = {}, {}, None
        scores = [0., 0., 0., 0.]
        neutral_message = ""
        if detected:
            points = result.face_landmarks[0]
            x = [p.x for p in points]
            y = [p.y for p in points]
            left = max(0, min(rgb.width - 1, int(min(x) * rgb.width)))
            top = max(0, min(rgb.height - 1, int(min(y) * rgb.height)))
            right = max(left + 1, min(rgb.width, int(max(x) * rgb.width) + 1))
            bottom = max(top + 1, min(rgb.height, int(max(y) * rgb.height) + 1))
            crop = rgb.crop((left, top, right, bottom))
            raw = {item.category_name: float(item.score) for item in result.face_blendshapes[0]}
            gesture, scores, adjusted = self.decision.decide(raw)
            if self._neutral_samples is not None:
                self._neutral_samples.append({name: raw[name] for name in FEATURES})
                neutral_message = f"Mantén el rostro relajado: {len(self._neutral_samples)}/{self._neutral_target} muestras."
                gesture = None
                if len(self._neutral_samples) >= self._neutral_target:
                    neutral = {name: float(np.median([row[name] for row in self._neutral_samples])) for name in FEATURES}
                    # Una expresión intensa no se acepta como referencia de reposo.
                    if any(value >= .80 for value in neutral.values()):
                        neutral_message = "No se guardó reposo: hay una activación alta. Relaja boca y cejas y vuelve a pulsar Ajustar reposo."
                    else:
                        self.decision = BlendshapeDecision(neutral)
                        self.neutral_path.parent.mkdir(parents=True, exist_ok=True)
                        self.neutral_path.write_text(json.dumps({"neutral": neutral}, indent=2), encoding="utf-8")
                        neutral_message = "Referencia de reposo guardada. Prueba ahora los cuatro gestos."
                    self._neutral_samples = None
        return {"gesture": gesture, "scores": scores, "face_detected": detected,
                "crop": crop, "input_image": crop.convert("L").resize((64, 64)),
                "milliseconds": (perf_counter() - started) * 1000,
                "score_kind": "intensidades", "signals": {name: raw.get(name) for name in FEATURES},
                "adjusted_signals": adjusted, "neutral_message": neutral_message,
                "calibrating_neutral": self._neutral_samples is not None}

    def predict(self, image):
        result = self.diagnose(image)
        return result["gesture"], result["scores"], result["face_detected"]

    def close(self):
        self.landmarker.close()
