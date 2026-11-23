# Revisión de la copia — 23 de noviembre de 2026

## Base y aislamiento

La copia parte del estado recibido después del merge, cuyo último commit observado fue `87dd6f4` (Implementacion del modelo de generacion completo y version final). El original estaba limpio al comenzar. No se copia `.git`, ni se hace commit o push. Se conserva fuera de esta carpeta un manifiesto SHA256 de los archivos originales para comprobar que no se modificaron.

## Limpieza aplicada

| Elemento | Decisión | Motivo |
|---|---|---|
| `tests/` | Conservar | Evidencia y regresión de interacción, inferencia y recuperación |
| `bloomface/metrics.py` | Conservar | Utilizado por pruebas y útil para la evaluación futura |
| Notebook floral activo | Conservar en `notebooks/` | El worker lee sus prompts y guías en ejecución |
| Notebook LibreFace | Mover a `docs/antecedentes/` | Piloto académico sin uso en la aplicación actual |
| Bitácora extensa | Archivar íntegra en antecedentes | Conservar evidencia y separar decisiones vigentes del historial |
| Fuentes Regular y TextBold | Mantener en carpeta activa | Son las variantes que carga la interfaz |
| Otras siete fuentes | Archivar con su aviso | Evitar empaquetarlas como recursos activos sin perder originales |
| Logo PNG / SVG | Conservar ambos | PNG activo y SVG maestro de diseño |

## Corrección de ejecución

El notebook recibido preparaba reconocimiento sin preparar el generador. Su primera celda ahora invoca el preparador portátil, que obtiene Python 3.12 y verifica ambos entornos. Se añade `preparar_floral.py` para crear la estructura que ya espera el código del merge (`floral_runtime/venv` y `weights/`). Las versiones de la interfaz y difusión permanecen separadas.

No se cambian DirectML/CPU, resoluciones, confirmación de tres segundos, guías, prompts, reglas de señales, diseño ni rondas. CUDA no se reintroduce en esta revisión. Se conserva `MPLBACKEND=Agg` del notebook recibido. Se añade un límite compatible de Hugging Face Hub para las bibliotecas de difusión legadas.

## Revisión previa a la integración

Abrir esta copia, revisar README y docs, ejecutar el notebook y la lista manual. Si se aprueba, trasladar únicamente fuentes, documentación, recursos y pruebas revisados, incluyendo los movimientos de antecedentes; no copiar entornos, pesos, `output/` ni `.git`. Hasta esa decisión, no se reemplaza ningún archivo del repositorio original.

Los resultados y pendientes concretos están en [VALIDACION](VALIDACION.md). La distribución del profesor debe asociarse a un paquete real que se haya probado; esta carpeta no sustituye esa comprobación.

## Revisión académica a partir del documento original

El 23 de noviembre de 2026 se incorporó como antecedente una copia íntegra de la propuesta enviada por Catalina. Se recuperaron el marco del macroproyecto y la problemática; se reformularon el objetivo general y tres objetivos específicos con acción, técnica y propósito. Se desarrollaron la justificación y las conclusiones, y se añadieron referencias y una correspondencia entre objetivos, evidencias y evaluación pendiente.

La metodología identifica las técnicas que realmente usa el proyecto, incluyendo la segmentación binaria de los pétalos del logo como apoyo gráfico. La CNN entrenada por el equipo permanece como antecedente. Esta revisión solo modifica documentación y añade el documento de referencia; conserva el código, el diseño, los modelos y las reglas de interacción.

## Integración autorizada en el repositorio principal

El 23 de noviembre de 2026, tras la revisión de la copia y con autorización del usuario, se trasladaron la documentación, la limpieza y las correcciones de preparación ya revisadas a la carpeta principal BloomFace. Las secciones anteriores describen el trabajo previo en la copia. Se conservaron el historial Git y el código de la aplicación, y se excluyeron entornos, pesos descargados y salidas temporales. Los antecedentes y las fuentes sin uso activo se archivaron sin perder su contenido. No se añadió el modo de evaluación ni un registro de participantes propuesto después. No se realizó commit ni push.
