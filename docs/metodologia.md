# Metodología e implementación

## Desarrollo y decisiones

| Etapa | Trabajo disponible | Papel en la versión actual |
|---|---|---|
| Exploración PDI | Filtros y variaciones de captura documentados en la bitácora | Orientan condiciones de prueba |
| Clasificación propia | CNN del Parcial 2 y pruebas internas históricas | Antecedente académico |
| Piloto de unidades de acción | LibreFace y cabeza entrenada sobre características | Antecedente conservado en notebook |
| Reconocimiento actual | MediaPipe Face Landmarker y reglas sobre blendshapes | Componente activo |
| Generación floral | SD 1.5, ControlNet Scribble y LCM-LoRA | Componente activo; cuatro etapas |
| Interacción e interfaz | Rondas, confirmación de tres segundos y diseño PySide6 | Versión posterior al merge |
| Distribución | Entornos separados y empaquetado PyInstaller | Arranque del código y construcción portátil |

El desarrollo evolucionó desde una propuesta de clasificación con CNN propia hacia la integración de MediaPipe y un generador floral condicionado. La metodología actual organiza la captura, el análisis facial, la confirmación y la generación como componentes de una misma experiencia artística. Los experimentos anteriores explican esa evolución; sus métricas se atribuyen a los modelos y condiciones en que se obtuvieron.

## Técnicas de procesamiento de imágenes y visión computacional

| Técnica | Implementación comprobable | Función en la experiencia |
|---|---|---|
| Adquisición y preparación de imágenes | OpenCV captura la webcam; se convierte a RGB y se ajusta el tamaño para la inferencia | Proporcionar fotogramas recientes con un formato consistente |
| Detección y análisis facial con aprendizaje automático | MediaPipe Face Landmarker produce landmarks y coeficientes de movimiento | Localizar información del rostro y representar movimientos visibles |
| Clasificación de gestos | Reglas propias sobre cinco coeficientes, referencia de reposo y posibilidad de abstención | Asignar las cuatro clases sin forzar una decisión en combinaciones ambiguas |
| Procesamiento temporal | Confirmación de tres segundos con marcas de captura y reinicio por interrupciones | Reducir activaciones por gestos transitorios y decidir cuándo solicitar una flor |
| Generación mediante aprendizaje profundo | SD 1.5, ControlNet Scribble y LCM-LoRA con guías de contorno y texto | Producir una respuesta floral condicionada por la etapa elegida |
| Segmentación binaria de un recurso gráfico | Máscara del canal alfa y componentes conectados en el símbolo del logo | Aislar los ocho pétalos utilizados en el indicador de espera de la interfaz |

La detección facial y la generación utilizan modelos preentrenados. La asignación final de los cuatro gestos combina sus señales con reglas del proyecto; no corresponde al entrenamiento de una CNN de cuatro salidas en esta versión. La segmentación binaria se emplea como apoyo gráfico de la interfaz y no constituye un segmentador semántico del rostro.

El conjunto integra varias de las categorías mencionadas en el enunciado del proyecto: procesamiento de imágenes, detección, clasificación y aprendizaje automático. Las funciones concretas y sus límites permiten justificar esa relación sin atribuir técnicas que no forman parte del recorrido implementado.

## Preparación y reconocimiento

El modelo recibe RGB con lado máximo de 640 píxeles, conservando proporción. El adaptador usa modo VIDEO, una cara y CPU. Las señales utilizadas son `mouthSmileLeft`, `mouthSmileRight`, `jawOpen`, `browDownLeft` y `browDownRight`. MediaPipe proporciona landmarks y coeficientes de expresión; la decisión de las cuatro clases es propia del proyecto. [Documentación oficial de Face Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker?tab=Python).

Se puede ajustar una referencia de reposo con la mediana de 16 muestras válidas. Cada señal se corrige mediante `clip((señal - referencia) / (1 - referencia), 0, 1)`. Una activación alta impide guardar un ajuste claramente expresivo. La referencia se guarda localmente y corresponde a la persona calibrada.

| Regla | Condición inicial después del ajuste |
|---|---|
| Sonrisa | Promedio de sonrisa ≥ 0,45 y ceño < 0,35 |
| Boca abierta | Mandíbula ≥ 0,45, sonrisa < 0,30 y ceño < 0,35 |
| Ceño fruncido | Mínimo de ambas cejas ≥ 0,35, sonrisa y mandíbula < 0,30 |
| Reposo | Máximo de sonrisa, mandíbula y ceño < 0,20 |
| Abstención | Cualquier combinación que no cumpla las reglas |

Las reglas se evalúan en el orden del código; la sonrisa con boca abierta puede seguir siendo sonrisa. Estos umbrales son iniciales y no se ha encontrado en la carpeta una evaluación con personas reservadas para esta versión.

## Confirmación y rondas

La clase `GestureConfirmation` exige tres segundos continuos del mismo gesto válido. Cambio de clase, rostro ausente, ambigüedad o un salto de más de un segundo entre muestras reinician el intento. El progreso proviene del reloj monotónico de captura y alimenta el borde animado.

Una confirmación produce una única solicitud floral. La ronda ignora nuevos gestos mientras se genera. Al llegar una imagen vigente, la interfaz pausa el reconocimiento y permite iniciar otra ronda desde cero. Una pausa manual invalida la solicitud pendiente y mantiene la composición existente.

## Generación condicionada

El worker lee del notebook floral las guías de contorno, descripciones, estilo y correspondencias entre expresión y etapa. ControlNet aporta el condicionamiento espacial; LCM-LoRA y `LCMScheduler` permiten el recorrido de cuatro pasos usado por el proyecto. El bucle combina ControlNet, UNet, scheduler y decodificación VAE; conserva el filtro de seguridad del modelo. [ControlNet en Diffusers 0.32.2](https://huggingface.co/docs/diffusers/v0.32.2/api/pipelines/controlnet), [LCM-LoRA publicado por sus autores](https://huggingface.co/latent-consistency/lcm-lora-sdv1-5).

DirectML emplea FP16 y 512 × 512. CPU emplea FP32, 384 × 384, dos hilos y atención del producto escalar de PyTorch. Las guías se redimensionan para CPU. Cada petición admite hasta dos semillas; si ninguna produce una imagen aceptada, se conserva la composición anterior y se permite otra ronda. [DirectML para PyTorch en Windows](https://learn.microsoft.com/en-us/windows/ai/directml/pytorch-windows).

## Procesamiento del recurso gráfico de espera

En `composition_view.py`, la función `_logo_petals` lee el canal alfa del logo, identifica el símbolo situado a la derecha del texto y crea una máscara binaria de sus píxeles visibles. `connectedComponentsWithStats`, con conectividad ocho, separa los componentes y obtiene sus dimensiones y centroides. El código espera ocho pétalos más el fondo, ordena los pétalos alrededor del centro y prepara cada imagen para la animación circular.

Este procedimiento aporta un ejemplo de umbralización y segmentación por componentes conectados aplicado a un recurso gráfico. Su función es comunicar la espera de la primera acuarela. [Documentación de componentes conectados de OpenCV](https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html).

## Reproducibilidad

El notebook de inicio prepara Python 3.12 y dos entornos aislados. Los pins de difusión se mantienen en `requirements-floral.txt`; la revisión limita Hugging Face Hub a una versión anterior a 1 para el conjunto de librerías legado. El preparador floral registra repositorios, revisiones y archivos descargados en `floral_runtime/procedencia_modelos.json`. Las comprobaciones y su alcance se registran en [resultados](resultados.md).

Las [referencias del proyecto](referencias.md) reúnen las fuentes conceptuales y la documentación de las técnicas utilizadas.
