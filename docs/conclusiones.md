# Conclusiones y proyección del proyecto

## Relación con el planteamiento

BloomFace concreta una experiencia de interacción entre expresión humana y representación de la naturaleza: los movimientos visibles del rostro seleccionan una etapa floral y dan lugar a una composición generada digitalmente. La correspondencia es una decisión artística que permite participar mediante el cuerpo y observar una respuesta visual. El alcance del sistema se expresa en términos de gestos observables y condiciones de captura definidas.

La implementación articula procesamiento de imágenes, análisis facial, clasificación por reglas, control temporal y generación condicionada. El uso de modelos preentrenados se complementa con decisiones propias sobre umbrales, confirmación, etapas florales, guías, estados de interacción y coordinación entre procesos. Esta integración constituye el aporte técnico implementado en la versión actual.

## Interpretación de los resultados

Las pruebas funcionales disponibles respaldan la lógica de los tres segundos, la selección de solicitudes, la interacción por rondas y la conservación de la composición. La revisión también comprobó el arranque desde el notebook y una solicitud real de reposo en CPU, que produjo una imagen de 384 × 384. Esa evidencia confirma la conexión entre el controlador y el generador para el caso ensayado; su protocolo y tiempos se presentan en [resultados](resultados.md).

La separación de procesos permite coordinar cámara, reconocimiento e interfaz mientras el generador realiza una tarea costosa. El respaldo en CPU ofrece una alternativa cuando DirectML no puede completar el trabajo. Las diferencias de resolución y tipo numérico entre perfiles, junto con la carga inicial del modelo, deben considerarse al interpretar los tiempos y comparar equipos.

La evaluación disponible todavía no establece la precisión del reconocedor actual ni la calidad de todas las etapas con personas y sesiones reservadas. Tampoco permite generalizar la latencia de una solicitud a cualquier PC. Las mediciones de CNN y LibreFace permanecen asociadas a sus experimentos históricos.

## Limitaciones

- Los umbrales de decisión necesitan evaluación con personas, sesiones y condiciones de captura diferentes. El habla y las combinaciones de movimientos pueden producir otra clase o una abstención.
- La referencia de reposo depende de la persona y de las condiciones en que se toma. Un encuadre que no incluya cejas y boca reduce la información disponible para la interacción.
- Las acuarelas se generan con semillas variables. La correspondencia entre etapas, la coherencia estilística y su aceptación visual requieren una evaluación específica; no se garantiza continuidad exacta entre imágenes.
- La difusión necesita memoria y recursos locales. El respaldo CPU amplía las opciones de ejecución, pero puede incrementar la espera.
- Las capturas documentales de la interfaz representan estados controlados. La prueba CPU real usa un gesto suministrado al controlador, sin webcam; el recorrido con participantes debe verificarse en los equipos de entrega.
- La entrega de un ejecutable requiere construir o localizar el paquete correcto y probarlo en otro Windows sin el entorno de desarrollo.

## Mejoras prioritarias

1. Evaluar los cuatro gestos, el habla, las mezclas y la ausencia de rostro con personas y sesiones reservadas, mediante matriz de confusión, recall, F1 macro y exactitud que contabilice los rechazos.
2. Medir por separado carga, inferencia facial, confirmación, generación y tiempo total hasta la imagen visible, registrando hardware, memoria y condiciones de prueba.
3. Registrar etapa, semilla, resolución, reintentos y aceptación por solicitud para analizar la diferenciación entre flores y su coherencia visual.
4. Revisar la experiencia con participantes para determinar si el encuadre, la indicación de progreso y la espera permiten comprender la relación entre gesto y resultado.
5. Validar el paquete portátil en un Windows limpio y documentar la versión exacta entregada al profesor.

Estas mejoras mantienen el propósito de relacionar expresión humana, naturaleza y creación visual, y proporcionan criterios para ampliar la evaluación técnica y de interacción del prototipo.
