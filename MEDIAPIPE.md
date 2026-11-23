# Reconocimiento facial actual

La aplicación usa MediaPipe Face Landmarker en CPU, modo VIDEO y RGB, con reglas explícitas para reposo, sonrisa, boca abierta y ceño. Las intensidades de movimiento no son probabilidades de las clases.

La especificación actual de señales, umbrales, referencia de reposo y confirmación de tres segundos está en [metodología](docs/metodologia.md). Las pruebas y limitaciones se describen en [resultados](docs/resultados.md).

La generación del merge utiliza DirectML con respaldo en CPU y se prepara automáticamente en la primera celda de la copia revisada. Las referencias anteriores a activación manual, CNN o LibreFace se conservan únicamente en [antecedentes](docs/antecedentes/README.md).
