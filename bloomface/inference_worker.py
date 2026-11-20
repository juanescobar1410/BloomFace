def run_classifier(connection):
    """Ejecuta la CNN en un proceso local con una entrada y una salida por fotograma."""
    try:
        import torch
        from PIL import Image

        from bloomface.classifier import GestureClassifier

        torch.set_num_threads(1)
        classifier = GestureClassifier()
        connection.send("ready")

        while True:
            width, height, stride, pixels = connection.recv()
            image = Image.frombytes("RGB", (width, height), pixels, "raw", "RGB", stride, 1)
            gesture, _, face_detected = classifier.predict(image)
            connection.send(("prediction", gesture, face_detected))
    except (EOFError, BrokenPipeError):
        pass
    except Exception as error:
        try:
            connection.send(("error", str(error) or type(error).__name__))
        except (EOFError, OSError):
            pass
    finally:
        connection.close()
