# BloomFace

BloomFace es el proyecto final de Procesamiento Digital de Imágenes de Catalina Ortiz González, Juan Andrés Escobar Sánchez y Juan David Romero Rada en la Universidad Autónoma de Occidente.

La aplicación de escritorio para Windows permitirá que una persona use la webcam para componer una flor con cuatro gestos visibles. En la muestra, la clasificación y la composición se ejecutarán en el PC.

| Gesto | Transformación |
|---|---|
| Reposo | Apertura intermedia y escala base. |
| Sonrisa | Apertura completa y escala base. |
| Boca abierta | Conserva la apertura visible al confirmar y aumenta la escala hasta un tamaño fijo. |
| Ceño fruncido | Cierra la flor y vuelve a la escala base. |

## Estado del proyecto

El repositorio comienza con la preparación del proyecto. Los cuadernos de los parciales son antecedentes de clasificación, segmentación y generación floral. La primera tarea de la aplicación será comprobar la webcam, el cambio floral con una sonrisa simulada y la pausa durante una transición.

## Desarrollo

- **Aplicación local.** Python, PySide6 con Qt Widgets, OpenCV y PyTorch.
- **Preparación de modelos y flores.** Cuadernos en Colab. La generación floral parte de Stable Diffusion 1.5 con DreamBooth y LoRA ajustado con fotografías propias.
- **Entrega para Windows.** Se prevé distribuir un ZIP con el ejecutable, la CNN y los recursos necesarios para una sesión local.

Las decisiones de interacción, la evidencia de los parciales y las tareas pendientes están en [CONTEXTO_BLOOMFACE.md](CONTEXTO_BLOOMFACE.md).

## Trabajo en equipo

Abrir la carpeta en GitHub Desktop mediante **File → Add local repository**. Antes del primer commit, verificar la cuenta y la identidad de Git. Los datos faciales se conservan fuera del repositorio y se comparten con los permisos acordados por el equipo.
