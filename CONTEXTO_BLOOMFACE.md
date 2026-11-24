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

[Descripción](docs/proyecto.md), [referencias](docs/referencias.md), [arquitectura](docs/arquitectura.md), [metodología](docs/metodologia.md), [instalación](docs/instalacion.md), [datos](docs/datos.md), [resultados](docs/resultados.md) y [bitácora histórica](docs/antecedentes/CONTEXTO_HISTORICO_2026-11-23.md).

## Evaluación exploratoria registrada

El equipo consignó 20 intentos con cinco participantes: 20/20 reconocimientos, imágenes y etapas correctas. Sin primera carga, el grupo GPU promedia 13,20 s (12 mediciones) y P4, registrado como CPU, 50,90 s (tres). La etiqueta del backend de P4 y el dato temporal J18 requieren revisión. El alcance y la fuente están en `docs/resultados.md`.

## Pendientes

Ampliar la evaluación exploratoria del reconocedor con más personas y condiciones, completar las evidencias y especificaciones de los ensayos, y validar un paquete portátil en otro Windows. La integración conserva el historial Git. No se ha hecho commit ni push. No se implementó el modo de evaluación propuesto posteriormente en el chat.

## Limpieza de documentación · 24 de noviembre de 2026

Se retiraron cuatro documentos auxiliares y sus enlaces de los Markdown. El documento de resultados conserva el ensayo con cinco participantes, las métricas, las evidencias y el ejemplo CPU. Se retiró la tabla de experimentos históricos.
