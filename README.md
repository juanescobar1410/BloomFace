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

Al abrirse la aplicación, pulsa **Iniciar** para ver las instrucciones. **Continuar** abre la pantalla principal y activa la cámara; todavía no inicia el reconocimiento. Ajusta el encuadre y pulsa **Iniciar** para comenzar a reconocer gestos. **Pausar** detiene el reconocimiento y **Reanudar** lo inicia de nuevo. **Finalizar** cierra la aplicación.

El único recurso facial requerido es `bloomface/models/mediapipe/face_landmarker.task`. Está fuera de Git y el notebook lo descarga si falta. No se necesitan `gestos_parcial2.pt`, `preprocesamiento.json` ni el XML Haar. No hay selector de modelos, entrenamiento ni calibración de la CNN. Las intensidades de sonrisa, mandíbula y cejas no son probabilidades. Consulta [MEDIAPIPE.md](MEDIAPIPE.md) para entender las reglas, límites y comprobaciones.

También se puede ejecutar `python preparar_mediapipe.py` y después `python -m bloomface` desde el entorno local. El reconocimiento funciona en CPU y en un proceso separado de la interfaz.

## Interfaz y estados

La interfaz tiene una pantalla de bienvenida, una pantalla de instrucciones y la pantalla principal. La cámara se abre al pulsar **Continuar**; el reconocimiento empieza únicamente al pulsar **Iniciar** en la pantalla principal. La vista principal muestra la cámara a la izquierda y deja el panel **Tu composición** disponible para la imagen generada.

El estado aparece en la etiqueta de la esquina superior derecha, por ejemplo **Vista Previa**, **Esperando gesto estable**, **Gesto estable: Sonrisa**, **En pausa** o **Rostro no detectado**. El recorte diagnóstico y las intensidades del modelo ya no se muestran en la interfaz. El aviso de rostro no detectado aparece tras tres muestras seguidas sin rostro y se quita después de dos detecciones seguidas. Los errores de cámara aparecen en el mismo panel bajo la vista de cámara e incluyen **Reintentar** y **Finalizar**.

Los botones **Ajustar reposo** y **Restablecer referencia** se conservan bajo la vista de cámara. Para fijar la referencia, inicia el reconocimiento, pulsa **Ajustar reposo** y mantén boca y cejas relajadas durante 16 muestras válidas. **Restablecer referencia** elimina el ajuste y detiene el reconocimiento; vuelve a pulsar **Iniciar** para comenzar otra vez.

El logo original está en `bloomface/assets/brand/BloomFace_Logo.svg`; la aplicación y el empaquetado usan su versión PNG transparente en `bloomface/assets/brand/BloomFace_Logo.png`. En ejecución local, la aplicación carga Agrandir desde `agrandir-font-family` si están disponibles `Agrandir-Regular.otf` y `Agrandir-TextBold.otf`. El archivo de licencia incluido indica uso personal únicamente; las fuentes no se agregan al paquete ejecutable.

## Generación floral

El cuaderno `notebooks/BloomFace_Generacion_Floral.ipynb` conserva las cuatro guías y permite probar la generación en Colab. La aplicación solicita una acuarela al confirmar un gesto. El proceso floral usa la guía correspondiente y devuelve la imagen en memoria. Si se pierde el rostro, se pausa o se confirma un gesto más reciente, se descarta la respuesta que haya quedado pendiente.

Para una futura validación en Windows, el generador requiere un entorno separado con `requirements-floral.txt` y los pesos públicos FP16 de SD 1.5 y ControlNet Scribble, además de LCM-LoRA. Usa `BLOOMFACE_FLORAL_RUNTIME` para señalar una carpeta con `venv/Scripts/python.exe` y pesos locales en `weights/sd15`, `weights/scribble` y `weights/lcm`. Esta versión de DirectML se probó con una RX 6600 XT. El interruptor `BLOOMFACE_ENABLE_LOCAL_GENERATOR=1` habilita el proceso cuando se decida retomar la validación del equipo.

Los resultados y las decisiones están en [CONTEXTO_BLOOMFACE.md](CONTEXTO_BLOOMFACE.md).

## Trabajo en equipo

Abrir la carpeta en GitHub Desktop mediante **File → Add local repository**. Antes del primer commit, verificar la cuenta y la identidad de Git. Los datos faciales se conservan fuera del repositorio y se comparten con los permisos acordados por el equipo.

Los notebooks originales de generación floral y LibreFace se conservan como antecedentes académicos; el notebook de LibreFace no es una ruta de ejecución de la aplicación.
