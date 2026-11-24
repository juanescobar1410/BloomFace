# Descripción del proyecto

## Contexto y problemática

En el marco del macroproyecto **Análisis de la Expresión Humana en el Arte y la Cultura**, BloomFace propone una experiencia artística en la que los gestos visibles del rostro intervienen en la creación de composiciones florales. La relación entre expresión humana, naturaleza y representación visual orienta la propuesta: una persona se sitúa frente a la cámara y participa en la composición mediante movimientos de su rostro.

La interacción entre el cuerpo y una respuesta digital tiene antecedentes en obras como *Text Rain*, de Romy Achituv y Camille Utterback, donde el movimiento de los participantes modifica elementos visuales proyectados. BloomFace retoma esa relación entre acción corporal y respuesta visual mediante una correspondencia entre gestos faciales y etapas de apertura de una flor. [Documentación de Text Rain](https://camilleutterback.com/projects/text-rain/).

La necesidad técnica consiste en distinguir reposo, sonrisa, boca abierta y ceño fruncido, y convertir la expresión confirmada en una respuesta floral coherente con la etapa asignada. Los fotogramas pueden variar por iluminación, posición y movimientos transitorios; además, la generación requiere un tiempo de procesamiento. La experiencia debe confirmar cuándo el gesto es estable, comunicar la espera y conservar un resultado válido ante interrupciones o fallos.

La pregunta que orienta el desarrollo es: **¿cómo transformar gestos faciales observables en composiciones florales generadas digitalmente, conservando una correspondencia comprensible entre la acción de la persona y el resultado visual dentro de una aplicación local?**

Las asociaciones entre gesto y flor son decisiones de diseño artístico. El alcance se limita a movimientos observables de una persona de frente a la webcam, con cejas y boca visibles e iluminación estable. La revisión de Barrett y colaboradores advierte que la relación entre movimientos faciales y categorías emocionales depende del contexto, las personas y la cultura; por ello, BloomFace describe sus entradas como gestos y delimita su interpretación. [Barrett et al., 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6640856/).

## Justificación

La propuesta articula el procesamiento de imágenes con una experiencia de creación visual. El rostro funciona como entrada de interacción y la flor como respuesta artística: ceño fruncido, reposo, sonrisa y boca abierta se relacionan con las etapas cerrada, punto medio, abierta y más abierta. Esta correspondencia permite observar el efecto de una acción corporal y repetir la experiencia mediante rondas sucesivas.

Desde el componente técnico, el proyecto integra adquisición de vídeo, preparación de imágenes, detección y análisis facial, reglas de clasificación, confirmación temporal y generación condicionada. Cada etapa cumple una función dentro del recorrido: la preparación estandariza la entrada del modelo; el análisis facial aporta señales de movimiento; las reglas y el tiempo de confirmación determinan cuándo actuar; y el generador produce la composición asociada al gesto elegido.

Los modelos preentrenados permiten desarrollar la integración sin repetir su entrenamiento. El aporte implementado por el equipo se concentra en seleccionar y combinar sus salidas, definir las correspondencias florales, coordinar los procesos y construir la interacción visual. La cámara y la interfaz continúan funcionando en componentes separados del generador, y la alternativa CPU permite ejecutar la difusión cuando DirectML no está disponible, con una espera mayor.

El procesamiento de la experiencia ocurre localmente después de preparar los recursos. La captura se utiliza en memoria y la composición permanece visible durante la sesión. Las pruebas funcionales, la documentación de instalación y el registro de las limitaciones permiten revisar el funcionamiento y preparar una demostración reproducible del proyecto.

## Objetivo general

Desarrollar un sistema interactivo de creación visual que vincule gestos faciales observables con la generación de composiciones florales, mediante técnicas de procesamiento digital de imágenes, visión computacional y modelos generativos preentrenados, para explorar posibilidades de interacción entre expresión humana, naturaleza y creación artística en una aplicación local de escritorio.

## Objetivos específicos

1. **Implementar un módulo de captura y análisis facial** que articule la preparación de fotogramas, la extracción de señales de movimiento con MediaPipe Face Landmarker y reglas de clasificación y confirmación temporal, para distinguir reposo, sonrisa, boca abierta y ceño fruncido bajo condiciones controladas de encuadre e iluminación.

2. **Integrar un proceso de generación floral condicionada** mediante Stable Diffusion 1.5, ControlNet Scribble y LCM-LoRA, utilizando guías de contorno y descripciones visuales para representar las cuatro etapas de apertura asociadas a los gestos y producir una composición por cada confirmación válida.

3. **Integrar el reconocimiento y la generación floral en una interfaz local por rondas**, con indicaciones de encuadre, confirmación, espera y resultado, y verificar su funcionamiento mediante pruebas de correspondencia gesto–flor, estabilidad temporal, tiempos de respuesta y recuperación ante fallos, para establecer los alcances y las limitaciones de la experiencia.

## Correspondencia entre objetivos y verificación

| Objetivo | Qué debe observarse | Evidencia disponible y alcance |
|---|---|---|
| Captura y análisis facial | Obtención de señales, decisión de las cuatro clases y reinicio ante interrupciones | Pruebas de reglas, tiempos e inferencia real sin rostro; falta evaluación con participantes |
| Generación condicionada | Solicitud de la etapa correspondiente y entrega de una imagen válida | Mapa de cuatro etapas, guías incluidas y una generación CPU real de reposo en esta revisión; falta evaluar la calidad de las cuatro etapas en una misma campaña |
| Integración y funcionamiento | Una imagen por ronda, controles, conservación de la composición y recuperación | Pruebas de interfaz y controlador, arranque del notebook y tiempo de una solicitud CPU; falta recorrido completo con webcam en los equipos de entrega |

Esta correspondencia distingue las comprobaciones funcionales realizadas de las evaluaciones pendientes. Los objetivos no implican que ya exista una cifra de precisión del reconocedor actual. El detalle de las pruebas y mediciones se presenta en [resultados](resultados.md).

## Solución y alcance actual

MediaPipe Face Landmarker obtiene información del rostro y coeficientes de movimiento. Las reglas del proyecto asignan esos coeficientes a los cuatro gestos o se abstienen cuando la combinación es ambigua. Un gesto debe mantenerse durante tres segundos continuos antes de seleccionar una etapa floral. El generador utiliza la guía y descripción correspondientes; la interfaz conserva la expresión elegida durante la generación y pausa la ronda al recibir la acuarela.

El recorrido actual genera imágenes a partir de modelos preentrenados y guías incluidas. La propuesta inicial contemplaba entrenar una CNN propia y transformar fotografías de flores; esas decisiones se conservan como antecedentes. La versión actual se documenta con su reconocimiento basado en MediaPipe y su generación por difusión, sin atribuirle entrenamiento o datos que no utiliza.

La aplicación está dirigida a Windows x64, una webcam y una persona frente a la cámara. DirectML trabaja a 512 × 512 en FP16 y el respaldo CPU a 384 × 384 en FP32. La disponibilidad de GPU, memoria y controladores afecta los tiempos de respuesta. La primera preparación necesita Internet; la inferencia utiliza los recursos locales después de descargarlos.

El planteamiento artístico y la problemática retoman la [propuesta inicial del equipo](antecedentes/Propuesta_original_BloomFace.docx). Las decisiones técnicas se corresponden con el código actual. Las fuentes conceptuales y técnicas se reúnen en [referencias](referencias.md).
