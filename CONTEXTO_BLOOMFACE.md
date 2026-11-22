# Contexto de desarrollo de BloomFace

Documento de referencia para el proyecto final de Procesamiento Digital de Imágenes de la Universidad Autónoma de Occidente. Revisar este archivo al iniciar cada tarea y actualizarlo cuando se apruebe una decisión, se cambie el alcance o se obtenga evidencia nueva. Registrar el resultado y su fuente. Los objetivos y los planes deben conservar su estado hasta que se verifiquen.

## Actualización aprobada — 22 de noviembre de 2026

La rama migra exclusivamente el reconocimiento facial a **MediaPipe Face Landmarker**. Esta decisión sustituye las referencias posteriores a CNN/LibreFace como reconocedores activos; esas secciones permanecen como historial. No se incluye selección de modelos ni reentrenamiento de la CNN. Se mantiene el generador DirectML original, sus prompts, notebook, entorno separado y activación explícita. No se trasladan los cambios de generación CPU de la otra carpeta.

El reconocimiento utiliza RGB, coeficientes de sonrisa/mandíbula/cejas, reglas explícitas y abstención en mezclas, con tres confirmaciones consecutivas y hasta ocho muestras por segundo. El ajuste opcional de reposo guarda 16 muestras válidas; no entrena el modelo. No se afirma precisión de participantes ni validación del ejecutable sin sus pruebas. Detalles y estado: `MEDIAPIPE.md`.

## Alcance aprobado

- BloomFace es una aplicación de escritorio para PC. El objetivo de producción es Windows. Una persona frente a la webcam del portátil compone una flor con gestos visibles y decide cuándo conservar la vista. La flor ocupa el panel principal y la cámara permite comprobar el encuadre. La etiqueta muestra el gesto confirmado.
- La sesión en vivo se ejecuta localmente. Colab se usa para preparar datos, entrenar y evaluar modelos, y generar de antemano las imágenes florales. El programa de la muestra carga la CNN y los recursos exportados.
- Las fases florales y las correspondencias entre gestos y efectos están cerradas. El punto 2 del Parcial 3, con Stable Diffusion 1.5, DreamBooth y LoRA sobre fotografías propias, es la base para producir el banco floral definitivo.
- El diseño final de Canva gobierna la presentación visual. El documento de los cuatro momentos gobierna las reglas de interacción cuando Canva no las especifica. El conector de Canva denegó acceso al diseño. Quedan por verificar la distribución exacta, la tipografía, la paleta, los rótulos y la representación visual de las fases.
- Conservar la composición significa mantenerla en pantalla durante la sesión. La experiencia clasifica gestos observables del rostro para componer la flor.

## Interacción y reglas florales

| Clase | Gesto | Efecto al confirmarse |
|---|---|---|
| 0 | Reposo | Apertura intermedia y escala base. |
| 1 | Sonrisa | Apertura completa y escala base. |
| 2 | Boca abierta | Conserva la apertura visible al confirmar y aumenta la escala hasta un objetivo absoluto. Sostener el gesto no acumula aumentos. |
| 3 | Ceño fruncido | Cierra la flor y vuelve a la escala base. |

El recorrido principal es **P1 Inicio → P2 Vista previa y encuadre → P3 Espera de gesto estable → P4 Resultado y exploración**. La guía de encuadre debe incluir cejas y boca. Un cambio de gesto pasa por la espera antes de modificar el objetivo floral.

Desde P3 o P4 se puede pasar a **P5 Pausa**. Se congelan la vista de cámara y la apertura y escala visibles, incluso a mitad de la transición. Reanudar regresa a P2 y exige confirmar de nuevo un gesto. **P6 Excepción** comunica un fallo y conserva la composición visible si existe. Un reintento exitoso vuelve a P2 después de recibir un fotograma válido. Si la lectura sigue fallando, se conserva P6. Finalizar vuelve a P1.

## Evidencia disponible

| Fuente | Qué aporta y qué queda por verificar |
|---|---|
| **Parcial 1** | Comparaciones visuales de filtros y simulaciones de iluminación, escala, distancia, perspectiva, ruido y movimiento. Orienta las pruebas de robustez. Sus etiquetas originales difieren de las cuatro clases de BloomFace. |
| **Parcial 2** | La CNN con Dropout + L2 obtuvo 94/96 aciertos (97,92 %) en la prueba interna. Las mismas tres personas aparecen en las distintas particiones y los dos errores corresponden a boca abierta. La generalización con personas reservadas sigue pendiente. |
| **Parcial 3, punto 1** | La U-Net con ResNet18 es una candidata para mejorar el recorte si la ROI guiada resulta insuficiente. Su aporte se debe medir por la conservación de cejas y boca, el rendimiento por gesto y la latencia local. |
| **Parcial 3, punto 2** | Stable Diffusion 1.5 con DreamBooth y LoRA se ajustó con 20 fotos propias de una flor amarilla. Hay resultados guardados que recuperan rasgos del ejemplar y otros con recortes o cambios de forma. Está pendiente validar un banco de estados compatibles del mismo ejemplar. |

La CNN del Parcial 2 con Haar, gris de 64×64 y StandardScaler documenta el primer prototipo y sus pruebas. El 19 de noviembre de 2026 el equipo decidió sustituir sus pesos en la versión final por una CNN preentrenada de terceros. LibreFace queda como antecedente. La aplicación de desarrollo usa la CNN propia del Parcial 2 en CPU.

## Investigación del clasificador preentrenado

- **Primer candidato para el piloto.** LibreFace ResNet-18 para estimar intensidades de unidades de acción facial, en la distribución oficial ONNX de OpenSense. Los artefactos son `LibreFace_AU_Encoder.onnx` y `LibreFace_AU_Intensity.onnx`. El segundo recibe las características del primero. La entrada documentada es un rostro alineado RGB de 224×224. ONNX Runtime ofrece un paquete CPU para Python 3.12 en Windows. [OpenSense](https://github.com/ihp-lab/OpenSense/tree/master/Utilities/LibreFace) · [ONNX Runtime](https://onnxruntime.ai/docs/install/#install-onnx-runtime-cpu)
- **Cuatro salidas de BloomFace.** AU4 orienta ceño fruncido, AU12 orienta sonrisa y AU25 y AU26 orientan boca abierta. Reposo requiere un rostro válido y valores bajos en los cuatro indicadores. Si hay gestos combinados, señales ambiguas o pérdida de encuadre, conservar la flor y reiniciar el conteo de confirmación. La cabeza de intensidad de LibreFace incluye AU25 y AU26. [Mapa de intensidades de OpenSense](https://github.com/ihp-lab/OpenSense/blob/master/Utilities/LibreFace/ActionUnitIntensityOutput.cs)
- **Candidatos comparados.** OpenGraphAU ResNet-18 publica pesos y las cuatro unidades requeridas. Py-Feat ConvNeXt V2 Tiny también publica esos indicadores y especifica uso de investigación no comercial para sus pesos. FER+ ofrece clases de emoción, con cobertura insuficiente de los movimientos específicos de BloomFace. [OpenGraphAU](https://github.com/lingjivoo/OpenGraphAU#pretrained-models) · [Py-Feat](https://huggingface.co/py-feat/face_multitask_v2) · [FER+](https://github.com/onnx/models/tree/main/validated/vision/body_analysis/emotion_ferplus)
- **Uso y redistribución.** Confirmar condiciones y avisos de los pesos antes de redistribuirlos. La licencia USC publicada contempla fines educativos, de investigación y sin ánimo de lucro con conservación de sus avisos. [Licencia del paquete oficial](https://www.nuget.org/packages/LibreFace/2.0.0/License)

## Piloto LibreFace · Resultados de la evaluación anterior

- **Datos.** La carpeta autorizada `Expresiones` aportó 898 imágenes únicas de 3 personas con una sesión por persona. Por clase hay 225 en reposo, 223 de sonrisa, 225 de boca abierta y 225 de ceño fruncido. Cuatro fotos sin identificador se excluyeron. Se separaron personas completas: 298 imágenes de entrenamiento, 300 de validación y 300 de prueba. El detector procesó las 898. La prueba cubre una sola persona y una sola sesión.
- **Modelo.** El encoder oficial ResNet-18 queda congelado y emite 512 características. Sobre ellas se entrena una cabeza de regresión logística multinomial con cuatro salidas (reposo, sonrisa, boca abierta, ceño fruncido). La política del piloto exige puntaje mínimo 0,65 y margen mínimo 0,20. Las intensidades AU descartan señales simultáneas fuertes de más de un gesto.
- **Resultados en la misma persona reservada.** Los resultados con abstención cuentan cada rechazo como error de la clase real.

| Método | F1 macro | Recall reposo | Recall sonrisa | Recall boca abierta | Recall ceño | Abstenciones |
|---|---:|---:|---:|---:|---:|---:|
| Reglas AU | 0,7282 | 100,0 % | 38,7 % | 57,3 % | 82,7 % | 34 |
| Cabeza, argmax | 0,7262 | 96,0 % | 62,7 % | 90,7 % | 42,7 % | 0 |
| Cabeza, política de la app | 0,6498 | 81,3 % | 53,3 % | 86,7 % | 18,7 % | 74 |

- **Paridad y tiempos.** Las ocho celdas de código se ejecutaron en Windows con Python 3.12.10. La exportación reprodujo los puntajes y las decisiones de las 300 imágenes de prueba, con una diferencia máxima de `1,79 × 10⁻⁷`. En terminal, la misma foto de referencia confirmó boca abierta (0,998214). En las imágenes válidas, preparación, encoder y AU tardaron una mediana de 45,2 ms y un P95 de 58,0 ms en CPU, sin lectura ni webcam. Queda pendiente ejecutar el cuaderno en Colab y comparar la misma referencia allí.
- **Interacción.** Con fotogramas suministrados en memoria a la entrada de cámara se verificaron los cuatro efectos, la congelación por pérdida de rostro, la abstención, el encuadre al reanudar y la liberación de la captura y del proceso al cerrar. La webcam física entregó fotogramas. Se comprobaron apertura, inicio de reconocimiento, pausa, reanudación y cierre sin participante. Una prueba con fotogramas discretos confirmó el reconocimiento en la tercera predicción consecutiva y el reinicio del conteo al perder el rostro. El piloto muestreaba hasta ocho fotogramas por segundo.
- **Pendientes.** Medir estabilidad y latencia en vivo con participantes y el portátil de la muestra. Evaluar habla y gestos combinados con secuencias anotadas. El ceño fruncido tuvo 14 aciertos de 75 con la política de la app. Priorizamos mejorar esa clase con más personas y sesiones antes de considerar el piloto apto para la muestra. Revisar también el banco floral, el ejecutable actualizado y el ZIP.
- **Archivos locales.** Los pesos oficiales, la cabeza ONNX y el JSON de configuración están en `bloomface/models/libreface` y están excluidos de Git. Las fotos se mantienen fuera del repositorio. El cuadernillo conserva salidas agregadas.

## Herramientas y entrega de PC

- El entorno local de desarrollo de BloomFace usa Python 3.12 en `.venv`. Se verificó Python 3.12.10 en Windows. El punto de entrada `python -m bloomface` abre la ventana con PySide6. OpenCV se instala con `opencv-contrib-python` junto con MediaPipe y PySide6 presenta la imagen.
- La aplicación actual usa **Python, PySide6 y OpenCV** para la interfaz, la composición y la vista previa de la webcam. Conserva la pausa y la reanudación. El espacio de composición inicia sin imagen. El reconocimiento se ejecuta en CPU y la generación DirectML queda desactivada por defecto.
- Preparar un paquete en carpeta con **PyInstaller**, generado en Windows. La entrega propuesta es `BloomFace-Windows.zip` con `BloomFace.exe`, dependencias, modelo, configuración y banco de imágenes. Documentar cómo se reproduce el empaquetado.
- El criterio de entrega es abrir el ejecutable con doble clic y completar la sesión con webcam, recursos incluidos y sin instalar Python, usar Colab o depender de internet. Validar primero en el equipo objetivo y después en un segundo Windows sin el entorno de desarrollo.
- La rúbrica también exige código y documentación en GitHub con README, arquitectura, metodología, instrucciones, datos o enlaces autorizados y resultados reproducibles. Los otros entregables son póster académico, video demostrativo de máximo tres minutos y sustentación oral con demostración.

## Orden de desarrollo recomendado

1. **Preparar el repositorio de GitHub.** Reutilizar el repositorio de BloomFace si el equipo ya tiene uno. Aprovechar el Git local de la carpeta para preparar el primer commit con un README breve, este contexto y un `.gitignore` para temporales, entornos, compilaciones y capturas faciales. Dar acceso a los integrantes y usar enlaces autorizados para compartir los datos que correspondan.
2. **Primera prueba local.** Abrir la webcam real en una ventana con cámara y flor. Conectar un gesto simulado al compositor. Probar sonrisa, avance de la apertura, pausa a mitad de la transición y regreso al encuadre. Usar imágenes florales provisionales alineadas para verificar el comportamiento.
3. **Prueba temprana de empaquetado.** Comprobar que una copia de la ventana con cámara y recursos abre desde el ejecutable en Windows. Registrar el equipo y las dependencias usadas.
4. **Clasificación y generación en paralelo.** Desde que el equipo tenga acceso al repositorio, inventariar y ampliar capturas autorizadas por persona y sesión. En la rama floral, inventariar fotos por fase, probar la generación del mismo ejemplar en las fases aprobadas y comprobar la alineación, incluidos los márgenes para ampliar la flor.
5. **Piloto con la CNN preentrenada.** La integración de LibreFace ONNX quedó como antecedente y se retiró de la ejecución de la aplicación. Antes de reactivarla, validar con participantes el recorrido webcam → gesto estable → cambio floral → pausa, con énfasis en ceño fruncido y abstenciones. Incorporar el banco definitivo y completar P1–P6.
6. **Validación y entrega.** Medir matriz de confusión, F1 macro, recall por clase, latencia y cambios involuntarios. Probar pérdida de encuadre, escala sin acumulación, pausa y recuperación de cámara. Validar la continuidad floral y preparar las evidencias de la rúbrica con la versión empaquetada.

## Estado inicial y decisiones pendientes

- El proyecto se inicializó en `E:\PDIProyectos\PROYECTO FINAL` y está vinculado al [repositorio privado BloomFace](https://github.com/juanescobar1410/BloomFace). Juan Andrés gestiona los commits desde GitHub Desktop. La ventana inicial está verificada. La vista previa abre la cámara bajo demanda, permite reintentar y libera el dispositivo al cerrar. La ventana carga los PNG provisionales desde `bloomface/assets/flowers`. En una prueba con esos archivos y una cámara simulada se verificaron la apertura inicial de 0,5, la transición al simular una sonrisa, la pausa con ambas vistas congeladas y la reanudación con una nueva acción. El prototipo inicial permitió simular los cuatro gestos. La interfaz del piloto de reconocimiento incluía Abrir cámara, Iniciar reconocimiento y Pausar o Reanudar. Durante el piloto, la flor cambiaba al confirmar un gesto. Se verificaron reposo a media apertura, sonrisa con apertura completa, ceño fruncido con cierre y boca abierta conservando la apertura visible incluso a mitad de una transición. Boca abierta lleva la escala a 1,15 en este prototipo, sin acumular ampliaciones al repetirla. Con los PNG provisionales se verificó que la ampliación no recorta la flor en las tres aperturas de referencia. La mezcla provisional deja contornos dobles donde los dibujos difieren. La prueba de integración en Windows recibió video de la webcam física e inició el reconocimiento. Juan Andrés confirmó que el primer ejecutable de Windows funcionó. El ZIP y un nuevo empaquetado con los pesos quedan pendientes. La CNN del Parcial 2 cargaba localmente los pesos, el scaler y el XML Haar en `bloomface/models`. Ese prototipo usaba OpenCV 4.13.0.92. En Windows, `prueba_002.jpeg` dio boca abierta con un puntaje softmax de 0,9999 y el detector encontró el rostro. La clase coincide con la salida guardada del cuaderno. La vista en vivo iniciaba el clasificador desde el encuadre. La CNN procesaba fotogramas recientes en un proceso local para mantener la interfaz receptiva y cerrar correctamente en Windows. El piloto toma hasta ocho muestras por segundo y exige tres predicciones consecutivas con rostro detectado. La ausencia de rostro reinicia el conteo y conserva la flor, y la pausa detiene el clasificador hasta un nuevo inicio. Se comprobó con la foto de referencia como entrada de video que Boca abierta amplía la flor, que la pausa conserva la composición y que al reanudar se exige una nueva confirmación. Los resultados de inferencia y de integración de este párrafo corresponden al prototipo del Parcial 2. La estabilidad y la latencia de extremo a extremo con personas se evaluarán con el piloto LibreFace.
- Falta confirmar el portátil, la webcam y la versión de Windows de la muestra, la disponibilidad de participantes y GPU, el acceso a las fotos y pesos originales, y la fecha de entrega.
- Deben validarse el recorte elegido, el número de fotogramas consecutivos o su duración efectiva, el factor de escala y la continuidad entre estados. Las metas del piloto son propuestas y aún no son resultados del sistema.

## Limpieza de la versión sin reconocimiento

- El código de inferencia desconectado, el PNG provisional sin referencias, las compilaciones anteriores, la caché y el entorno descartado de Python 3.15 se retiraron de la carpeta de trabajo. El entorno activo usa Python 3.12.
- Se conservaron los modelos locales fuera de Git, el cuadernillo y las evidencias del piloto. La especificación de PyInstaller sigue disponible para el siguiente empaquetado.

## Investigación de difusión para el banco floral · 20 de noviembre de 2026

El criterio del piloto es obtener las fases cerrada, semiabierta y abierta del mismo ejemplar amarillo, con fondo, encuadre, tallo y hojas estables. El gesto de boca abierta activa una ampliación en la aplicación. Conviene generar y revisar los recursos en un entorno separado y usar los PNG aprobados en Windows.

| Modelo | Evidencia y pertinencia |
|---|---|
| SD 1.5 con DreamBooth y LoRA del Parcial 3 | Se localizó el archivo final `entrenamiento_fp16_corregido/pytorch_lora_weights.safetensors` de 3,23 MB en la carpeta local del Parcial 3. El cuaderno documenta el modelo base y el ajuste con las fotos propias. Es el primer candidato para conservar los rasgos de la flor. Falta verificar las tres aperturas en un mismo encuadre. [Modelo base](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5) |
| Flower BLIP LoRA | El API de Hugging Face confirmó el adaptador `pytorch_lora_weights.safetensors`. La ficha declara 2.000 imágenes florales con descripciones BLIP, 512 × 512 y CreativeML OpenRAIL-M. Es el comparador externo más práctico por usar SD 1.5. La ficha muestra comparaciones visuales y carece de una prueba de las tres fases del mismo ejemplar. [Ficha](https://huggingface.co/imaquantinizer/sd15-flower-blip-lora) |
| Anthos-1 | El API confirmó `model.safetensors`. La ficha declara 256 × 256, 102 clases Oxford, Apache 2.0 y evaluación visual. La entrada elige una categoría floral. Sirve como referencia de generación especializada. [Ficha](https://huggingface.co/Glint-Research/Anthos-1) |
| DDPM Flowers 64 y Flower UNet2D | Modelos incondicionales de 64 × 64 y 32 × 32. El DDPM de Anton tiene pesos públicos confirmados y licencia Apache 2.0. Ambos sirven para ilustrar el efecto de entrenar en flores, con escaso control y resolución para el banco visual. [DDPM de Diffusers](https://huggingface.co/docs/diffusers/v0.14.0/en/training/unconditional_training) · [Flower UNet2D](https://huggingface.co/pop123ux/Flower-UNet2D-pipeline) |
| Floral Diffusion y LoRA de lavanda | Floral Diffusion publica enlaces a un checkpoint de Disco Diffusion y el hash esperado. Usa un cuaderno heredado. La adaptación de lavanda documenta control por etapa y datos de esa especie con FLUX.1 dev. Ambas demuestran especialización floral con poca pertinencia para el ejemplar amarillo. [Floral Diffusion](https://github.com/jags111/floral-diffusion) · [Lavanda](https://huggingface.co/Potiron/lavender-flux) |
| Dinámica de floración | DynamiCrafter publica pesos y muestra una flor abriéndose a partir de una imagen. Su variante de interpolación recibe dos extremos y los autores reportan 12,8 GB de memoria en su prueba. Free-Bloom presenta floración guiada por texto. Birth and Death of a Rose y Latent State Machines estudian la continuidad 4D del crecimiento. La página de Rose anuncia acceso por solicitud y la de LSM enlaza el artículo sin pesos públicos en la página consultada. [DynamiCrafter](https://github.com/Doubiiu/DynamiCrafter) · [Free-Bloom](https://proceedings.neurips.cc/paper_files/paper/2023/hash/52f050499cf82fa8efb588e263f6f3a7-Abstract.html) · [Rose](https://chen-geng.com/rose4d/) · [LSM](https://yuegao.me/lsm/) |

Primera comparación propuesta en Colab con GPU: SD 1.5 con la foto y la máscara como referencia, el mismo flujo con el LoRA propio y el mismo flujo con Flower BLIP por separado. Usar las mismas semillas y fijar el recorte y las instrucciones de cada fase. Una máscara debe abarcar la corola y el espacio donde crecerá. Si la forma sigue variando, probar una guía de contorno por fase. Verificar que el tallo y el fondo queden fijos al recomponer con la referencia. Evaluar fidelidad del ejemplar, separación de fases, continuidad en la transición y proporción de imágenes aceptadas. Se verificaron las fuentes y el archivo local. La comparación de imágenes está pendiente. [Edición con máscaras](https://huggingface.co/docs/diffusers/using-diffusers/inpaint) · [ControlNet Canny](https://huggingface.co/lllyasviel/control_v11p_sd15_canny)

## Generador floral bajo demanda

- BloomFace generará una acuarela nueva al confirmar cada expresión. El cuaderno usa Stable Diffusion 1.5, ControlNet Scribble y LCM-LoRA con 4 pasos de inferencia. Cerrada corresponde a ceño fruncido, punto medio a reposo, abierta a sonrisa y más abierta a boca abierta.
- En Colab, el flujo anterior produjo las cuatro aperturas con la semilla 83. La prueba de reintento tomó 5,31 s con el modelo cargado. La primera semilla fue marcada por el filtro y la segunda produjo la flor. La prueba simulada de dos fallos conservó la imagen anterior.
- El cuaderno limpio está en `notebooks/BloomFace_Generacion_Floral.ipynb`. Conserva las cuatro guías, un reintento máximo y la generación en memoria. El archivo pasó la validación estructural y una ejecución simulada local. Está pendiente repetir la inferencia del cuaderno limpio en Colab y probar el flujo en Windows.
- En Windows, DirectML ejecutó una prueba sintética FP16 de convolución, residual y proyección matricial en la AMD Radeon RX 6600 XT de 8 GiB. El perfil de ONNX Runtime 1.24.4 registró los dos nodos fusionados en DirectML y los resultados coincidieron con la referencia numérica dentro de la tolerancia. En 30 corridas la mediana fue 0,35 ms y el P95 fue 0,60 ms. La prueba solo mide ese grafo.
- En Windows se generó una acuarela de punto medio a 512 × 512 con la guía y el prompt del cuaderno, semilla 83 y cuatro pasos LCM. La carga de pesos locales tomó 8,22 s y la generación completa con modelo cargado tomó 12,07 s. Los pesos se cargaron en un entorno de prueba con PyTorch 2.4.1 y DirectML. ControlNet, UNet y VAE usaron la Radeon y el filtro se ejecutó en CPU. La salida mostró pétalos levantados y separados, con aspecto de acuarela. Esta prueba cubrió una imagen y todavía falta medir la latencia desde el gesto en la aplicación.

### BloomFace-prueba-CNN con generación en vivo

- La copia local situada en E:\PDIProyectos\BloomFace-prueba-CNN conecta la CNN propia del Parcial 2 con el generador floral. Al iniciar reconocimiento se carga el generador en un proceso aparte. Cada gesto confirmado solicita una imagen nueva de la etapa correspondiente. La aplicación mantiene la última flor visible y descarta los resultados atrasados al cambiar de gesto, pausar o perder el rostro.
- La prueba completa con la foto de referencia suministrada al flujo de cámara confirmó boca abierta y mostró una acuarela para la etapa más abierta. El proceso floral tardó 9,7 s en esa solicitud y la vista recibió fotogramas mientras tanto. También se verificaron la pausa, el cierre y la liberación de recursos. La webcam física entregó fotogramas. Los cuatro gestos con un participante quedan pendientes de probar.
- Para iniciar desde PowerShell, abre la carpeta de la copia de prueba y ejecuta el Python de la carpeta principal con el módulo bloomface. La copia usa los pesos públicos ya descargados en el entorno separado de DirectML.

- Los PNG provisionales de Paint y el código que los cargaba se retiraron de ambas copias. La copia de prueba inicia con un mensaje y muestra una flor cuando llega la primera acuarela generada. El empaquetado deja de incluir la carpeta floral provisional.

### Integración en el repositorio principal

- La CNN del Parcial 2, la confirmación de gestos y el generador bajo demanda se incorporaron al repositorio principal. Las acuarelas se entregan en memoria y los PNG de Paint se retiraron.
- El generador DirectML queda desactivado por defecto tras dos apagados inesperados en Windows. El modo de prueba normal usa la webcam y la CNN en CPU. La conexión entre gesto y acuarela se verifica con un generador simulado mientras se aclara la estabilidad de la GPU.

## Fuentes de referencia

- [Diseño final en Canva](https://www.canva.com/design/DAHYlN678yk/xu-UQVXdE6QBwdvlswayRQ/edit)
- `BloomFace_Sesion_12_Cuatro_Momentos (2).docx`
- `BloomFace_ProyectoFinal_EscobarOritzRomero (2).docx`
- `Rubrica proyecto final PDI 2026-2.pdf`
- `Parcial_1_PDI_Punto_1_16_Variaciones_Aleatorias.ipynb`
- `Parcial_2_PDI_OrtizEscobarRomero (3).ipynb`
- `Parcial3-EscobarOrtizRomero 3.ipynb`

### Aplicación directa en la carpeta principal · 22 de noviembre de 2026

- Se aplicó la integración MediaPipe en `C:\Users\juand\OneDrive\Desktop\BloomFace` después de comprobar que Git no mostraba cambios locales pendientes. Se creó el respaldo `C:\Users\juand\OneDrive\Desktop\Trabajo pdi\BloomFace_integracion_respaldos\antes_mediapipe_20261122_170907_809097.zip`. No se hizo commit, push ni cambio de rama.
- Se preparó `.venv` con Python 3.12 y el bundle facial local. Se unificó OpenCV en `opencv-contrib-python`, requerido por MediaPipe, evitando instalar simultáneamente `opencv-python`.
- Evidencia local: `preparar_mediapipe.py --check-only` completó carga e inferencia real sin rostro y `pip check` sin dependencias rotas. `python -m unittest discover -s tests -v` pasó las 23 pruebas en el nuevo entorno. `git diff --check` no detectó errores de formato.
- La comparación con Git confirmó que `camera.py`, `floral.py`, `floral_worker.py`, `requirements-floral.txt` y los notebooks originales permanecen intactos. El generador conserva su configuración desactivada por defecto. No se probó webcam, precisión con participantes ni generación GPU en esta sesión.


### Preparación portátil desde el notebook

La primera celda ejecuta preparar_notebook.py con biblioteca estándar, localiza el repositorio sin rutas personales, crea o reutiliza .venv, prepara las dependencias y comprueba el modelo. Un kernel incompatible puede obtener Python 3.12 mediante uv de PyPI, con recursos bajo output. El notebook vuelve a metadata genérica Python 3: no exige el kernel local BloomFace. VS Code sí necesita un kernel funcional para ejecutar la primera celda.

Validación: se ejecutó la primera celda en una copia sin .venv ni modelos, desde Python 3.15.2. Obtuvo CPython 3.12.16 mediante uv, creó .venv, instaló dependencias, descargó el modelo y completó inferencia real sin rostro y pip check. También se ejecutaron todas las celdas con el kernel Jupyter disponible y se verificó el inicio de Qt en modo offscreen, cerrando el proceso de prueba. Pasaron las 23 pruebas de regresión. No se probó webcam ni generación GPU. Los cambios siguen locales, sin commit ni push.
