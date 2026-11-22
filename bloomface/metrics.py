"""Métricas sin dependencias: filas reales, columnas predichas y rechazo."""
from bloomface.decision import CLASSES


def classification_report(truth, predicted):
    if len(truth) != len(predicted) or not truth:
        raise ValueError("Se requieren listas no vacías de igual longitud")
    matrix = [[0] * 5 for _ in CLASSES]
    for actual, guess in zip(truth, predicted):
        if actual not in CLASSES or (guess is not None and guess not in CLASSES):
            raise ValueError("Etiqueta desconocida")
        matrix[CLASSES.index(actual)][4 if guess is None else CLASSES.index(guess)] += 1
    recalls, f1 = {}, []
    for i, label in enumerate(CLASSES):
        tp = matrix[i][i]
        support = sum(matrix[i])
        fp = sum(row[i] for j, row in enumerate(matrix) if j != i)
        fn = support - tp  # Incluye los rechazos.
        recalls[label] = tp / support if support else None
        f1.append(2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0)
    return {"classes": list(CLASSES), "columns": [*CLASSES, "rechazo"],
            "confusion_matrix": matrix, "n": len(truth),
            "f1_macro_4_classes": sum(f1) / 4, "recall": recalls,
            "accuracy_including_rejections": sum(matrix[i][i] for i in range(4)) / len(truth),
            "rejections": sum(row[4] for row in matrix),
            "support": {label: sum(matrix[i]) for i, label in enumerate(CLASSES)}}
