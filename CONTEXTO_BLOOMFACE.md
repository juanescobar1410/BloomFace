# Contexto vigente de BloomFace

Fecha: 23 de noviembre de 2026. Base observada: commit `87dd6f4` del proyecto posterior al merge. La documentación, organización y preparación revisadas en una copia se integraron en el repositorio principal con autorización del usuario el 23 de noviembre de 2026.

## Estado actual

- Aplicación Windows x64 en Python, PySide6 y OpenCV.
- MediaPipe Face Landmarker es el único reconocedor activo; reglas sobre cinco señales, referencia opcional de reposo y abstención.
- Confirmación continua de tres segundos por reloj monotónico; una flor por ronda, pausa al mostrar resultado y nuevo Iniciar para otra ronda.
- SD 1.5 + ControlNet Scribble + LCM-LoRA, cuatro pasos y filtro conservado. DirectML a 512 px FP16; respaldo en CPU a 384 px FP32.
- Interfaz del merge, borde de confirmación y animación de ocho pétalos conservados.
- Notebook revisado prepara ambos entornos y modelos. El contexto anterior completo está archivado y no debe usarse como instrucción vigente.

## Marco académico vigente

El planteamiento se sitúa en Análisis de la Expresión Humana en el Arte y la Cultura. La propuesta original se conserva en `docs/antecedentes/Propuesta_original_BloomFace.docx`. La documentación actual recupera su problemática y desarrolla tres objetivos específicos para captura y análisis, generación condicionada e integración y verificación. Las técnicas y fuentes se explican en metodología y referencias. La clasificación describe gestos observables; las correspondencias florales son decisiones artísticas.

## Fuentes de referencia

[Descripción](docs/proyecto.md), [referencias](docs/referencias.md), [arquitectura](docs/arquitectura.md), [metodología](docs/metodologia.md), [instalación](docs/instalacion.md), [datos](docs/datos.md), [resultados](docs/resultados.md), [revisión](docs/revision.md), [validación](docs/VALIDACION.md) y [bitácora histórica](docs/antecedentes/CONTEXTO_HISTORICO_2026-11-23.md).

## Pendientes

Prueba con participantes y webcam, evaluación del reconocedor actual y validación de un paquete portátil en otro Windows. La documentación registra resultados anteriores con su procedencia; no les atribuye precisión al modelo actual. La integración conserva el historial Git. No se ha hecho commit ni push. No se implementó el modo de evaluación propuesto posteriormente en el chat.
