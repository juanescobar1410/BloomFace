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

La aplicación de Windows usa la CNN del Parcial 2 para confirmar gestos. El generador floral está integrado y queda desactivado por defecto tras dos apagados durante las pruebas de la Radeon. En este modo se puede probar la webcam y el reconocimiento usando CPU.

## Ejecutar en Windows

Desde la carpeta del repositorio, con Python 3.12 y un entorno `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m bloomface
```

Para iniciar el reconocimiento, coloca `gestos_parcial2.pt`, `preprocesamiento.json` y `haarcascade_frontalface_default.xml` en `bloomface/models`. Git ignora esa carpeta. En la ventana, selecciona **Abrir cámara** y luego **Iniciar reconocimiento**.

## Generación floral

El cuaderno `notebooks/BloomFace_Generacion_Floral.ipynb` conserva las cuatro guías y permite probar la generación en Colab. La aplicación solicita una acuarela al confirmar un gesto. El proceso floral usa la guía correspondiente y devuelve la imagen en memoria. Si se pierde el rostro, se pausa o se confirma un gesto más reciente, se descarta la respuesta que haya quedado pendiente.

Para una futura validación en Windows, el generador requiere un entorno separado con `requirements-floral.txt` y los pesos públicos FP16 de SD 1.5 y ControlNet Scribble, además de LCM-LoRA. Usa `BLOOMFACE_FLORAL_RUNTIME` para señalar una carpeta con `venv/Scripts/python.exe` y pesos locales en `weights/sd15`, `weights/scribble` y `weights/lcm`. Esta versión de DirectML se probó con una RX 6600 XT. El interruptor `BLOOMFACE_ENABLE_LOCAL_GENERATOR=1` habilita el proceso cuando se decida retomar la validación del equipo.

Los resultados y las decisiones están en [CONTEXTO_BLOOMFACE.md](CONTEXTO_BLOOMFACE.md).

## Trabajo en equipo

Abrir la carpeta en GitHub Desktop mediante **File → Add local repository**. Antes del primer commit, verificar la cuenta y la identidad de Git. Los datos faciales se conservan fuera del repositorio y se comparten con los permisos acordados por el equipo.
