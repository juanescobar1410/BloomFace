# Validación de la copia de revisión

Este informe conserva las comprobaciones realizadas en la copia antes de integrar. La documentación y los cambios revisados se trasladaron después al repositorio principal con autorización del usuario; la afirmación de integridad del original que sigue corresponde al momento anterior a ese traslado.

Fecha: 23 de noviembre de 2026. Base: `87dd6f4`. Todas las modificaciones de esta entrega se realizaron en la copia. El repositorio original conserva **46 archivos idénticos por SHA256**, sin archivos añadidos o retirados fuera de `.git`. Se conserva el [manifiesto original](evidencias/original_sha256.json).

| Comprobación | Resultado y alcance |
|---|---|
| Suite automatizada | **39/39 correctas, sin omisiones**. 34 del merge y cinco nuevas de preparación. [Registro](evidencias/pruebas_automatizadas.txt) |
| MediaPipe real | Bundle cargado en proceso hijo, imagen sin rostro y cierre comprobados por la suite. No evalúa gestos con participantes |
| Entorno de reconocimiento | `.venv` creado en la copia, dependencias instaladas, `pip check` y prueba facial correctos |
| Entorno floral | `floral_runtime/venv` creado, PyTorch 2.4.1 CPU + DirectML y librerías de difusión importan; `pip check` correcto |
| Modelos florales | Descarga de los archivos requeridos; repositorios y revisiones en `floral_runtime/procedencia_modelos.json` |
| Instalación desde ausencia de entornos | Se crearon ambos entornos y modelos en la copia. Se corrigió y probó la salida Unicode de la consola al retomar la descarga |
| Notebook completo | Todas las celdas ejecutadas con Jupyter real; preparó ambos entornos, abrió Qt en modo offscreen y se comprobó que el proceso seguía vivo. La prueba cerró el proceso |
| Generación CPU real | PNG 384 × 384; 21.59 s de inferencia; 42.14 s con carga; sin webcam, gesto suministrado al controlador |
| Preservación funcional | Código de `bloomface/`, logo y notebook floral activo idénticos a la fuente; solo cambia preparación, organización y documentación |
| Capturas | Cinco estados de Qt sin webcam, etiquetados como evidencia controlada; ilustración de demostración distinguida de la acuarela real |
| Diagramas | PNG y SVG revisados visualmente y Mermaid incluido; componentes y recorrido derivados del código |
| Enlaces internos y sintaxis | Comprobación final en [auditoría JSON](evidencias/auditoria.json) |

## Qué no se ha validado aquí

No se activó la webcam física, no se evaluaron personas, no se midió precisión facial actual ni se probó difusión completa con GPU DirectML. La recuperación GPU → CPU se comprobó mediante los dobles de la suite. No se reconstruyó un ejecutable ni se ensayó un Windows limpio. Las mediciones históricas del README anterior se atribuyen a su bitácora.

## Protocolo utilizado antes de integrar

1. Abrir esta carpeta como proyecto y leer README, documentación y cambios de organización.
2. Ejecutar el notebook; los entornos y pesos ya están preparados en esta máquina, pero pueden requerir recreación al trasladar la carpeta a otro equipo.
3. Probar los cuatro gestos y rondas con webcam mediante la lista de `verificacion.md`.
4. Confirmar que objetivos, datos y conclusiones representan el trabajo del equipo.
5. Si se aprueba integrar, trasladar las fuentes revisadas; evitar copiar `.venv`, `floral_runtime`, `output` o historial Git.

El ZIP de código y documentación que acompaña esta copia excluye entornos y pesos. **No es un portátil ejecutable**; al extraerlo en otro PC, Run All prepara los recursos.

## Actualización de redacción académica

Se revisaron problemática, justificación, objetivos, metodología y conclusiones a partir de la propuesta original aportada por el equipo. Se conservaron los resultados y sus límites. El código y los recursos activos de la copia mantienen sus hashes; no se repitieron pruebas de inferencia porque no hubo cambios funcionales. Se verificaron enlaces internos y la coherencia de las tres formulaciones de objetivos.
