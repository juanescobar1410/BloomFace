# BloomFace

BloomFace es el proyecto final de Procesamiento Digital de Imágenes de Catalina Ortiz González, Juan Andrés Escobar Sánchez y Juan David Romero Rada en la Universidad Autónoma de Occidente.

La aplicación de escritorio para Windows permitirá que una persona use la webcam para componer una flor con cuatro gestos visibles. En la muestra, la clasificación y la composición se ejecutarán en el PC.

| Gesto | Transformación |
|---|---|
| Ceño fruncido | Flor cerrada. |
| Reposo | Punto medio o semiabierta. |
| Sonrisa | Flor abierta. |
| Boca abierta | Flor más abierta, con los pétalos extendidos hacia los lados. |

## Estado del proyecto

La aplicación de Windows usa MediaPipe Face Landmarker para reconocer los cuatro gestos. La generación floral usa Stable Diffusion 1.5, ControlNet Scribble y LCM-LoRA. En Windows intenta usar DirectML (GPU) y, cuando no está disponible o falla, continúa en CPU.

## Distribución portátil para Windows x64

Extrae el ZIP completo y abre `BloomFace.exe` dentro de la carpeta `BloomFace`. El paquete contiene Python, las dependencias, el modelo facial y los pesos de difusión. La generación se habilita automáticamente al iniciar el reconocimiento y funciona sin conexión.

Pulsa **INICIAR** y avanza con **→**. En la vista previa pulsa **Iniciar**. BloomFace intenta usar una GPU compatible con DirectML y cambia a CPU si no está disponible o falla. Mantén un gesto durante 3 segundos para solicitar una acuarela. El brillo del borde de la cámara avanza por ambos lados y se cierra en verde al confirmar el gesto. La primera imagen incluye el tiempo de carga del modelo. La aplicación toma un solo gesto por ronda. Cuando muestra la flor, pasa a pausa y conserva la composición. Pulsa el mismo botón **Iniciar** y mantén un gesto durante tres segundos para generar la siguiente.

## Ejecutar en Windows

Abre la carpeta completa del repositorio en VS Code local y ejecuta **Run All / Ejecutar todo** en `BloomFace_Instalar_y_Probar.ipynb`. Puedes usar cualquier kernel Python local funcional: la primera celda crea o reutiliza el entorno compatible de la aplicación, instala dependencias y descarga y verifica el modelo. Si el Python del kernel no es compatible, obtiene Python 3.12 automáticamente mediante uv. Después abre BloomFace. No usa rutas de un equipo concreto ni requiere un kernel llamado BloomFace. Necesita Internet la primera vez.

Requisitos previos del notebook: Windows de 64 bits, VS Code con extensiones Python y Jupyter y un kernel Python con `ipykernel`. Si VS Code ofrece instalar ipykernel antes de ejecutar, acepta **Instalar**; ninguna celda puede instalar su propio kernel antes de empezar a ejecutarse. La preparación de la aplicación ocurre en `.venv` y no instala MediaPipe en el entorno del kernel. [Gestión automática de Python con uv](https://docs.astral.sh/uv/guides/install-python/).

En la ventana pulsa **INICIAR → flecha → Iniciar**. Para establecer tu referencia personal pulsa **Ajustar reposo (rostro relajado)** y mantén boca y cejas relajadas durante 16 muestras con rostro detectado. **Restablecer referencia de reposo** borra ese ajuste y exige iniciar de nuevo reconocimiento.

El único recurso facial requerido es `bloomface/models/mediapipe/face_landmarker.task`. Está fuera de Git y el notebook lo descarga si falta. No se necesitan `gestos_parcial2.pt`, `preprocesamiento.json` ni el XML Haar. No hay selector de modelos, entrenamiento ni calibración de la CNN. Las intensidades de sonrisa, mandíbula y cejas no son probabilidades. Consulta [MEDIAPIPE.md](MEDIAPIPE.md) para entender las reglas, límites y comprobaciones.

También se puede ejecutar `python preparar_mediapipe.py` y después `python -m bloomface` desde el entorno local. El reconocimiento funciona en CPU y en un proceso separado de la interfaz.

## Generación floral

El cuaderno `notebooks/BloomFace_Generacion_Floral.ipynb` conserva las cuatro guías y permite probar la generación en Colab. La aplicación solicita una acuarela al confirmar un gesto. El proceso floral usa la guía correspondiente y devuelve la imagen en memoria. El perfil GPU genera a 512 × 512 en FP16. El perfil CPU genera a 384 × 384 en FP32 con dos hilos. Ambos usan cuatro pasos. Si falla la inicialización o el proceso de GPU, el generador reinicia en CPU y recupera el último gesto vigente. En el equipo de prueba el generador alcanzó 8,09 GiB de RAM y tardó de 21,89 a 43,68 segundos por flor, con el modelo cargado. Mientras se genera una flor, la ronda conserva su gesto confirmado. Una pausa manual cancela la solicitud pendiente.

Para construir el portátil desde el código, prepara el entorno de interfaz con PyInstaller y el modelo facial. Prepara aparte un entorno floral con Python 3.12 de 64 bits y `requirements-floral.txt`. La carpeta floral debe contener `venv/Scripts/python.exe` y los pesos ya descargados en `weights/sd15`, `weights/scribble` y `weights/lcm`.

```powershell
.\.venv\Scripts\python.exe empaquetar_portatil.py --floral-runtime "C:\ruta\al\entorno-floral" --zip
```

El resultado se guarda en `dist/`. Para ejecutar desde el código con ese mismo entorno, configura `BLOOMFACE_FLORAL_RUNTIME` con la ruta a la carpeta floral antes de abrir la aplicación.

Los resultados y las decisiones están en [CONTEXTO_BLOOMFACE.md](CONTEXTO_BLOOMFACE.md).

## Trabajo en equipo

Abrir la carpeta en GitHub Desktop mediante **File → Add local repository**. Antes del primer commit, verificar la cuenta y la identidad de Git. Los datos faciales se conservan fuera del repositorio y se comparten con los permisos acordados por el equipo.

Los notebooks originales de generación floral y LibreFace se conservan como antecedentes académicos; el notebook de LibreFace no es una ruta de ejecución de la aplicación.
