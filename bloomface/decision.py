"""Confirmación temporal independiente de Qt y del modelo."""
CLASSES = ("reposo", "sonrisa", "boca_abierta", "ceno_fruncido")
WAITING_FOR_GESTURE = "waiting"
NO_FACE = "no_face"


CONFIRMATION_NS = 3_000_000_000
MAX_SAMPLE_GAP_NS = 1_000_000_000


class GestureConfirmation:
    def __init__(self):
        self.reset()

    def reset(self):
        self.candidate = None
        self.started_at_ns = None
        self.last_sample_ns = None

    @property
    def progress(self):
        if self.started_at_ns is None:
            return 0.0
        return min(1.0, (self.last_sample_ns - self.started_at_ns) / CONFIRMATION_NS)

    def update(self, gesture, face_detected, sample_ns):
        if not face_detected:
            self.reset()
            return NO_FACE
        if gesture is None:
            self.reset()
            return WAITING_FOR_GESTURE
        if gesture not in CLASSES:
            raise ValueError(f"Gesto desconocido: {gesture}")

        if (self.candidate != gesture
                or sample_ns - self.last_sample_ns > MAX_SAMPLE_GAP_NS):
            self.candidate = gesture
            self.started_at_ns = sample_ns
        self.last_sample_ns = sample_ns
        return gesture if self.progress == 1.0 else WAITING_FOR_GESTURE
