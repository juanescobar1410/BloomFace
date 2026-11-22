def run_classifier(connection):
    """Reconocedor seleccionado en un proceso local, sin bloquear Qt."""
    classifier = None
    try:
        from PIL import Image
        from bloomface.classifier import GestureClassifier
        classifier = GestureClassifier()
        connection.send("ready")

        while True:
            message = connection.recv()
            if len(message) == 2 and message[0] == "calibrate_neutral":
                if not hasattr(classifier, "begin_neutral_calibration"):
                    raise ValueError("La referencia de reposo sólo está disponible en MediaPipe.")
                classifier.begin_neutral_calibration()
                message = message[1]
            width, height, stride, pixels = message
            image = Image.frombytes("RGB", (width, height), pixels, "raw", "RGB", stride, 1)
            result = classifier.diagnose(image)
            connection.send(("prediction", result["gesture"], result["face_detected"],
                             result["scores"], result["milliseconds"],
                             result["input_image"].tobytes(),
                             classifier.model_label,
                             {key: result.get(key) for key in
                              ("score_kind", "signals", "neutral_message", "calibrating_neutral")}))
    except (EOFError, BrokenPipeError):
        pass
    except Exception as error:
        try:
            connection.send(("error", str(error) or type(error).__name__))
        except (EOFError, OSError):
            pass
    finally:
        try:
            if classifier is not None:
                classifier.close()
        finally:
            connection.close()
