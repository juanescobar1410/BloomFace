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

El clasificador del Parcial 2 usa recorte Haar, gris de 64×64, `StandardScaler` y una CNN de 6/16 canales. La propuesta documentada usa ROI fija, gris de 64×64, normalización `/255` y una CNN de 16/32 canales. Comparar las dos configuraciones con los mismos grupos de personas y sesiones, seleccionar con validación y evaluar al final en la prueba reservada. El modelo exportado requiere el mismo contrato de preparación durante la ejecución. Si se adopta el modelo con scaler, incluir los parámetros ajustados con entrenamiento.

## Herramientas y entrega de PC

- La combinación propuesta es **Python, PySide6 con Qt Widgets, OpenCV y PyTorch**. PySide6 presenta la interfaz, OpenCV gestiona la cámara y el procesamiento de imágenes, y PyTorch ejecuta la CNN. Medir primero la inferencia en CPU en el portátil objetivo.
- Preparar un paquete en carpeta con **PyInstaller**, generado en Windows. La entrega propuesta es `BloomFace-Windows.zip` con `BloomFace.exe`, dependencias, modelo, configuración y banco de imágenes. Documentar cómo se reproduce el empaquetado.
- El criterio de entrega es abrir el ejecutable con doble clic y completar la sesión con webcam, recursos incluidos y sin instalar Python, usar Colab o depender de internet. Validar primero en el equipo objetivo y después en un segundo Windows sin el entorno de desarrollo.
- La rúbrica también exige código y documentación en GitHub con README, arquitectura, metodología, instrucciones, datos o enlaces autorizados y resultados reproducibles. Los otros entregables son póster académico, video demostrativo de máximo tres minutos y sustentación oral con demostración.

## Orden de desarrollo recomendado

1. **Preparar el repositorio de GitHub.** Reutilizar el repositorio de BloomFace si el equipo ya tiene uno. Aprovechar el Git local de la carpeta para preparar el primer commit con un README breve, este contexto y un `.gitignore` para temporales, entornos, compilaciones y capturas faciales. Dar acceso a los integrantes y usar enlaces autorizados para compartir los datos que correspondan.
2. **Primera prueba local.** Abrir la webcam real en una ventana con cámara y flor. Conectar un gesto simulado al compositor. Probar sonrisa, avance de la apertura, pausa a mitad de la transición y regreso al encuadre. Usar imágenes florales provisionales alineadas para verificar el comportamiento.
3. **Prueba temprana de empaquetado.** Comprobar que una copia de la ventana con cámara y recursos abre desde el ejecutable en Windows. Registrar el equipo y las dependencias usadas.
4. **Clasificación y generación en paralelo.** Desde que el equipo tenga acceso al repositorio, inventariar y ampliar capturas autorizadas por persona y sesión. En la rama floral, inventariar fotos por fase, probar la generación del mismo ejemplar en las fases aprobadas y comprobar la alineación, incluidos los márgenes para ampliar la flor.
5. **Primera integración real.** Sustituir el gesto simulado por la CNN seleccionada y confirmar el recorrido webcam → gesto estable → cambio floral → pausa. Incorporar el banco definitivo y completar P1–P6.
6. **Validación y entrega.** Medir matriz de confusión, F1 macro, recall por clase, latencia y cambios involuntarios. Probar pérdida de encuadre, escala sin acumulación, pausa y recuperación de cámara. Validar la continuidad floral y preparar las evidencias de la rúbrica con la versión empaquetada.

## Estado inicial y decisiones pendientes

- El proyecto se inicializó en `E:\PDIProyectos\PROYECTO FINAL` y está vinculado al [repositorio privado BloomFace](https://github.com/juanescobar1410/BloomFace). El README, el contexto y las reglas de exclusión están pendientes del primer commit. Juan Andrés hará los commits desde GitHub Desktop. La primera prueba local, el ejecutable y la integración en Windows están pendientes.
- Falta confirmar el portátil, la webcam y la versión de Windows de la muestra, la disponibilidad de participantes y GPU, el acceso a las fotos y pesos originales, y la fecha de entrega.
- Deben validarse el recorte elegido, el número de fotogramas consecutivos o su duración efectiva, el factor de escala y la continuidad entre estados. Las metas del piloto son propuestas y aún no son resultados del sistema.

## Fuentes de referencia

- [Diseño final en Canva](https://www.canva.com/design/DAHYlN678yk/xu-UQVXdE6QBwdvlswayRQ/edit)
- `BloomFace_Sesion_12_Cuatro_Momentos (2).docx`
- `BloomFace_ProyectoFinal_EscobarOritzRomero (2).docx`
- `Rubrica proyecto final PDI 2026-2.pdf`
- `Parcial_1_PDI_Punto_1_16_Variaciones_Aleatorias.ipynb`
- `Parcial_2_PDI_OrtizEscobarRomero (3).ipynb`
- `Parcial3-EscobarOrtizRomero 3.ipynb`
