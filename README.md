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

La aplicación de Windows usa exclusivamente **MediaPipe Face Landmarker** para reconocer los cuatro gestos; no carga la CNN del Parcial 2 ni LibreFace. El generador floral está integrado y queda desactivado por defecto tras dos apagados durante las pruebas de la Radeon. En este modo se puede probar la webcam y el reconocimiento usando CPU.

## Ejecutar en Windows

Abre la carpeta completa del repositorio en VS Code local y ejecuta **Run All / Ejecutar todo** en `BloomFace_Instalar_y_Probar.ipynb`. Puedes usar cualquier kernel Python local funcional: la primera celda crea o reutiliza el entorno compatible de la aplicación, instala dependencias y descarga y verifica el modelo. Si el Python del kernel no es compatible, obtiene Python 3.12 automáticamente mediante uv. Después abre BloomFace. No usa rutas de un equipo concreto ni requiere un kernel llamado BloomFace. Necesita Internet la primera vez.

Requisitos previos del notebook: Windows de 64 bits, VS Code con extensiones Python y Jupyter y un kernel Python con `ipykernel`. Si VS Code ofrece instalar ipykernel antes de ejecutar, acepta **Instalar**; ninguna celda puede instalar su propio kernel antes de empezar a ejecutarse. La preparación de la aplicación ocurre en `.venv` y no instala MediaPipe en el entorno del kernel. [Gestión automática de Python con uv](https://docs.astral.sh/uv/guides/install-python/).

En la ventana pulsa **Abrir cámara → Iniciar reconocimiento**. Para establecer tu referencia personal pulsa **Ajustar reposo (rostro relajado)** y mantén boca y cejas relajadas durante 16 muestras con rostro detectado. **Restablecer referencia de reposo** borra ese ajuste y exige iniciar de nuevo reconocimiento.

El único recurso facial requerido es `bloomface/models/mediapipe/face_landmarker.task`. Está fuera de Git y el notebook lo descarga si falta. No se necesitan `gestos_parcial2.pt`, `preprocesamiento.json` ni el XML Haar. No hay selector de modelos, entrenamiento ni calibración de la CNN. Las intensidades de sonrisa, mandíbula y cejas no son probabilidades. Consulta [MEDIAPIPE.md](MEDIAPIPE.md) para entender las reglas, límites y comprobaciones.

También se puede ejecutar `python preparar_mediapipe.py` y después `python -m bloomface` desde el entorno local. El reconocimiento funciona en CPU y en un proceso separado de la interfaz.

## Generación floral

El cuaderno `notebooks/BloomFace_Generacion_Floral.ipynb` conserva las cuatro guías y permite probar la generación en Colab. La aplicación solicita una acuarela al confirmar un gesto. El proceso floral usa la guía correspondiente y devuelve la imagen en memoria. Si se pierde el rostro, se pausa o se confirma un gesto más reciente, se descarta la respuesta que haya quedado pendiente.

Para una futura validación en Windows, el generador requiere un entorno separado con `requirements-floral.txt` y los pesos públicos FP16 de SD 1.5 y ControlNet Scribble, además de LCM-LoRA. Usa `BLOOMFACE_FLORAL_RUNTIME` para señalar una carpeta con `venv/Scripts/python.exe` y pesos locales en `weights/sd15`, `weights/scribble` y `weights/lcm`. Esta versión de DirectML se probó con una RX 6600 XT. El interruptor `BLOOMFACE_ENABLE_LOCAL_GENERATOR=1` habilita el proceso cuando se decida retomar la validación del equipo.

Los resultados y las decisiones están en [CONTEXTO_BLOOMFACE.md](CONTEXTO_BLOOMFACE.md).

## Trabajo en equipo

Abrir la carpeta en GitHub Desktop mediante **File → Add local repository**. Antes del primer commit, verificar la cuenta y la identidad de Git. Los datos faciales se conservan fuera del repositorio y se comparten con los permisos acordados por el equipo.

Los notebooks originales de generación floral y LibreFace se conservan como antecedentes académicos; el notebook de LibreFace no es una ruta de ejecución de la aplicación.
