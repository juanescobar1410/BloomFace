"""Confirmación temporal independiente de Qt y del modelo."""
CLASSES = ("reposo", "sonrisa", "boca_abierta", "ceno_fruncido")
WAITING_FOR_GESTURE = "waiting"
NO_FACE = "no_face"


class GestureConfirmation:
    def __init__(self, frames=3):
        if frames < 1:
            raise ValueError("frames debe ser positivo")
        self.frames = frames
        self.reset()

    def reset(self):
        self.candidate = None
        self.repetitions = 0

    def update(self, gesture, face_detected):
        if not face_detected:
            self.reset()
            return NO_FACE
        if gesture is None:
            self.reset()
            return WAITING_FOR_GESTURE
        if gesture not in CLASSES:
            raise ValueError(f"Gesto desconocido: {gesture}")
        if self.candidate != gesture:
            self.candidate = gesture
            self.repetitions = 0
        self.repetitions = min(self.repetitions + 1, self.frames)
        return gesture if self.repetitions == self.frames else WAITING_FOR_GESTURE
