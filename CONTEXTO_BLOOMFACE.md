# Contexto de desarrollo de BloomFace

Documento de referencia para el proyecto final de Procesamiento Digital de Imágenes de la Universidad Autónoma de Occidente. Revisar este archivo al iniciar cada tarea y actualizarlo cuando se apruebe una decisión, se cambie el alcance o se obtenga evidencia nueva. Registrar el resultado y su fuente. Los objetivos y los planes deben conservar su estado hasta que se verifiquen.

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

La CNN del Parcial 2 con Haar, gris de 64×64 y StandardScaler documenta el primer prototipo y sus pruebas. El 19 de noviembre de 2026 el equipo decidió sustituir sus pesos en la versión final por una CNN preentrenada de terceros. LibreFace y la CNN anterior quedan como antecedentes. La aplicación de desarrollo se ejecuta sin clasificador activo.

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
- La aplicación actual usa **Python, PySide6 y OpenCV** para la interfaz, la composición y la vista previa de la webcam. Conserva la pausa y la reanudación. La flor se muestra a media apertura y los modelos permanecen guardados para pruebas posteriores.
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

## Fuentes de referencia

- [Diseño final en Canva](https://www.canva.com/design/DAHYlN678yk/xu-UQVXdE6QBwdvlswayRQ/edit)
- `BloomFace_Sesion_12_Cuatro_Momentos (2).docx`
- `BloomFace_ProyectoFinal_EscobarOritzRomero (2).docx`
- `Rubrica proyecto final PDI 2026-2.pdf`
- `Parcial_1_PDI_Punto_1_16_Variaciones_Aleatorias.ipynb`
- `Parcial_2_PDI_OrtizEscobarRomero (3).ipynb`
- `Parcial3-EscobarOrtizRomero 3.ipynb`
