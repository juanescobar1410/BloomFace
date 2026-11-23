# Resultados y análisis

## Cómo interpretar la evidencia

Se distinguen tres fuentes: código inspeccionado, resultados registrados en la bitácora anterior y comprobaciones ejecutadas sobre esta copia. Los resultados de un modelo anterior o una prueba con señales controladas no se convierten en precisión facial de la aplicación actual.

## Resultados históricos registrados

| Experimento / equipo | Resultado registrado | Alcance |
|---|---|---|
| CNN del Parcial 2 | 94/96 aciertos; 97,92 % | Prueba interna histórica con personas compartidas entre particiones; modelo retirado de la app |
| LibreFace con reglas AU | F1 macro 0,7282; 34 abstenciones | Prueba de 300 imágenes de una sola persona reservada, según bitácora |
| Cabeza LibreFace con política de app | F1 macro 0,6498; 74 abstenciones | Piloto anterior; tampoco corresponde al reconocedor MediaPipe |
| CPU Ryzen 5 5600X, 31,92 GiB RAM, perfil elegido 384 px | Cerrada 24,05 s; punto medio 22,74 s; abierta 21,89 s; más abierta 43,68 s | Cuatro resultados descritos con modelo cargado |
| Mismo perfil CPU | Carga 25,87 s; pico 8,09 GiB en el generador | Medición histórica de ese entorno |
| Recuperación GPU → CPU | Acuarela de sonrisa 384 px en widget; 49,36 s; 8,11 GiB | Ensayo registrado con fallo de GPU reproducido |
| Interfaz y confirmación | Bitácora registra 34 pruebas antes de esta revisión | Se vuelve a ejecutar la suite y se registra el resultado real debajo |

Fuente de esta tabla: [bitácora histórica conservada](antecedentes/CONTEXTO_HISTORICO_2026-11-23.md). Los artefactos de esas mediciones no están todos incluidos en la carpeta recibida, por lo que la tabla se atribuye a la bitácora, sin afirmar una nueva reproducción.

## Comprobaciones de esta copia

El informe de ejecución se guarda en [validación de la revisión](VALIDACION.md). Incluye resultado de la suite, comprobación de recursos, capturas Qt y comparación de hashes del original. Las capturas de interfaz usan estados controlados sin webcam.

## Ejemplo real medido en esta copia

![Acuarela generada en CPU a partir de la etapa de reposo](evidencias/06_acuarela_cpu_real.png)

Se solicitó **reposo** directamente al controlador floral, con el worker y pesos reales, sin webcam ni participante. Se recibió un PNG de 384 × 384. La generación con modelo cargado tardó **21.59 s**; el recorrido de prueba, incluida la carga, tardó **42.14 s**. Equipo: AMD Ryzen 7 7435HS, 23,69 GiB de RAM instalada, Windows 11 y Python 3.12.14. Se forzó CPU en el controlador de prueba; el código de la aplicación mantiene su selección DirectML/CPU.

Este ejemplo confirma una solicitud real y la entrega al controlador. No mide la precisión del gesto, la latencia desde una persona frente a cámara ni la calidad de las cuatro etapas. Los tiempos no deben generalizarse a otros PC. El [registro JSON](evidencias/generacion_cpu.json) conserva protocolo, dimensiones y tiempos.

## Métricas y evaluación pendiente

La utilidad `classification_report` calcula matriz de confusión con una columna de rechazo, exactitud contando rechazos como errores, F1 macro de cuatro clases, recall por clase y soportes. Las pruebas de esa utilidad comprueban el cálculo; no suministran un conjunto de evaluación real del reconocedor actual.

No se encontró una matriz de confusión con personas y sesiones reservadas para MediaPipe y estos umbrales. Por eso no se publica una exactitud global de la versión final. El protocolo propuesto está en [verificación](verificacion.md).

Para latencia deben medirse por separado: carga, inferencia facial, confirmación de tres segundos, generación con modelo cargado y tiempo total hasta la imagen visible. Las cifras de CPU y GPU de resoluciones distintas no permiten comparar únicamente la velocidad del dispositivo. La mayor espera de Más abierta puede incluir un reintento del filtro; el registro disponible no permite atribuir causalidad exacta.
