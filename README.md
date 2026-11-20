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

La versión actual muestra la vista previa de la webcam y la flor a media apertura, con controles de pausa y reanudación. El reconocimiento automático está desactivado.

## Ejecutar en Windows

En PowerShell, desde la carpeta del proyecto, con Python 3.12 en `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m bloomface
```

En la ventana, selecciona **Abrir cámara**. Usa **Pausar** para congelar la vista previa y **Reanudar** para volver al video en vivo. La flor conserva su estado inicial.

## Cuadernillo y modelos guardados

El cuadernillo `notebooks/BloomFace_LibreFace_Clasificacion.ipynb` conserva el entrenamiento y la evaluación de LibreFace. Los archivos de los modelos siguen en `bloomface/models` para el trabajo posterior. La aplicación de escritorio funciona con las dependencias de `requirements.txt`.

La generación floral sigue el Parcial 3 con Stable Diffusion 1.5 y DreamBooth con LoRA. El ZIP y la actualización del ejecutable quedan pendientes. Las decisiones y las métricas están en [CONTEXTO_BLOOMFACE.md](CONTEXTO_BLOOMFACE.md).

## Trabajo en equipo

Abrir la carpeta en GitHub Desktop mediante **File → Add local repository**. Antes del primer commit, verificar la cuenta y la identidad de Git. Los datos faciales se conservan fuera del repositorio y se comparten con los permisos acordados por el equipo.
