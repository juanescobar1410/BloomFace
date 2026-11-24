# Conclusiones y proyección del proyecto

## Relación con el planteamiento

BloomFace concreta una experiencia de interacción entre expresión humana y representación de la naturaleza: los movimientos visibles del rostro seleccionan una etapa floral y dan lugar a una composición generada digitalmente. La correspondencia es una decisión artística que permite participar mediante el cuerpo y observar una respuesta visual. El alcance del sistema se expresa en términos de gestos observables y condiciones de captura definidas.

La implementación articula procesamiento de imágenes, análisis facial, clasificación por reglas, control temporal y generación condicionada. El uso de modelos preentrenados se complementa con decisiones propias sobre umbrales, confirmación, etapas florales, guías, estados de interacción y coordinación entre procesos. Esta integración constituye el aporte técnico implementado en la versión actual.

## Interpretación de los resultados

En la evaluación exploratoria del equipo participaron cinco personas y se registraron 20 intentos. En todos se confirmó el gesto solicitado, se mostró una imagen y se anotó la etapa floral esperada. Estos resultados respaldan el recorrido gesto–generación–etapa floral en las condiciones ensayadas y los objetivos de captura, generación e integración. El 100 % corresponde a esos 20 intentos, no a una garantía de precisión en otros usuarios o contextos.

Los tiempos sin primera carga promediaron 13,20 s en 12 mediciones anotadas con GPU dedicada y 50,90 s en tres mediciones de P4, registrado como CPU. La relación de 3,86 entre promedios describe una mayor espera en P4; no demuestra una diferencia causada únicamente por el dispositivo. La expresión «CPU de gráficos integrados» debe aclararse y faltan especificaciones de hardware. La primera carga se analiza aparte; el dato de P5–ceño está almacenado como fecha y no permite publicar un promedio inicial válido. Las fuentes y cálculos se presentan en [resultados](resultados.md#evaluación-exploratoria-con-cinco-participantes).

Las pruebas automatizadas y las comprobaciones técnicas complementan el registro de participantes: cubren confirmación temporal, rondas, recuperación y conexión entre controlador y generador. La separación de procesos permite coordinar captura e interfaz durante una tarea costosa. El respaldo CPU amplía las opciones de ejecución, con una espera que debe comunicarse mediante indicaciones de carga y progreso.

La muestra no establece precisión general del reconocedor, calidad artística de todas las imágenes ni estabilidad entre repeticiones. Las mediciones de CNN y LibreFace permanecen asociadas a sus experimentos históricos y no se combinan con los 20 intentos de la versión actual.

Durante la revisión visual, el equipo señaló que las imágenes asociadas a **boca abierta (etapa más abierta)** resultaban más extrañas que las de las otras etapas. Esta es una observación cualitativa: no se registró una valoración estética por intento ni una frecuencia de esa percepción. El cumplimiento de la etapa esperada no implica que la imagen tenga una calidad visual satisfactoria.

## Limitaciones

- La prueba incluye cinco personas y una repetición por gesto; los grupos son desiguales (16 intentos con GPU dedicada y cuatro en P4). Los umbrales de decisión necesitan evaluación con más personas, sesiones y condiciones de captura diferentes. El habla y las combinaciones de movimientos pueden producir otra clase o una abstención.
- La referencia de reposo depende de la persona y de las condiciones en que se toma. Un encuadre que no incluya cejas y boca reduce la información disponible para la interacción.
- Las acuarelas se generan con semillas variables. La correspondencia entre etapas, la coherencia estilística y su aceptación visual requieren una evaluación específica; no se garantiza continuidad exacta entre imágenes.
- La difusión necesita memoria y recursos locales. El respaldo CPU amplía las opciones de ejecución, pero puede incrementar la espera.
- Las capturas documentales previas representan estados controlados y la prueba técnica CPU suministra el gesto al controlador. Los 20 intentos con participantes se documentan mediante registro manual; el [video demostrativo](https://drive.google.com/drive/folders/1QnlKGPzSLxmXWYSKPR-9ky_ccc3YyCzO?usp=drive_link) y las [evidencias visuales](https://drive.google.com/drive/folders/1roSEUYetW253kGcOQmd0Q32GxQD35YFs?usp=sharing) están disponibles mediante las carpetas aportadas por el equipo, pero faltan su asociación con cada intento y las condiciones de prueba. Deben confirmarse el backend de P4 y las marcas de primera carga, y corregirse el tiempo guardado como fecha en J18.
- La entrega de un ejecutable requiere construir o localizar el paquete correcto y probarlo en otro Windows sin el entorno de desarrollo.

## Mejoras prioritarias

1. Ampliar la prueba de los cuatro gestos e incluir el habla, las mezclas y la ausencia de rostro con personas y sesiones reservadas, mediante matriz de confusión, recall, F1 macro y exactitud que contabilice los rechazos.
2. Medir por separado carga, inferencia facial, confirmación, generación y tiempo total hasta la imagen visible, registrando hardware, memoria y condiciones de prueba.
3. Revisar las guías de contorno y las descripciones de boca abierta (etapa más abierta), cuya apariencia fue percibida por el equipo como más extraña. Comparar distintas semillas y registrar etapa, resolución, reintentos y aceptación visual para evaluar si los ajustes mejoran el resultado, sin asumir una causa antes de comprobarla.
4. Revisar la experiencia con participantes para determinar si el encuadre, la indicación de progreso y la espera permiten comprender la relación entre gesto y resultado.
5. Validar el paquete portátil en un Windows limpio y documentar la versión exacta entregada al profesor.

Estas mejoras mantienen el propósito de relacionar expresión humana, naturaleza y creación visual, y proporcionan criterios para ampliar la evaluación técnica y de interacción del prototipo.
