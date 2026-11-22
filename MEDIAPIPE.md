# Reconocimiento exclusivo con MediaPipe Face Landmarker

La aplicación usa un único reconocedor: `bloomface/classifier.py` implementa `GestureClassifier` con MediaPipe Tasks en CPU y modo VIDEO. No contiene GestureCNN, Haar, estandarización de 4096 píxeles, cabeza de clasificación entrenable ni rutas a LibreFace. PyTorch queda sólo en el generador floral, que conserva su entorno separado original.

## Uso local

Abre `BloomFace_Instalar_y_Probar.ipynb` en VS Code, selecciona Python 3.12 y pulsa Ejecutar todo. Se prepara `.venv`, se instalan `requirements.txt` y se obtiene `bloomface/models/mediapipe/face_landmarker.task`. El instalador comprueba su carga real y ausencia de rostro sobre una imagen negra. La primera descarga necesita Internet; los siguientes inicios reutilizan archivos locales. La procedencia y SHA256 de la descarga están junto al modelo en `face_landmarker.json`.

Abre cámara, inicia reconocimiento y opcionalmente pulsa Ajustar reposo manteniendo rostro relajado durante 16 muestras válidas (al menos unos dos segundos, según CPU). Se guarda la mediana de cada señal en `bloomface/models/mediapipe/reposo.json`. No compartir esa referencia entre personas. Restablecer referencia elimina ese JSON; vuelve a iniciar reconocimiento. Una expresión intensa no debe usarse como reposo.

## Entrada, decisión y salida

El modelo recibe RGB con lado máximo de 640 conservando proporción. El recorte gris de 64 × 64 de la interfaz es sólo una referencia visual. Los coeficientes de movimiento no son probabilidades ni suman uno. Cada señal se corrige como `clip((señal - reposo)/(1 - reposo), 0, 1)`; sin referencia se usa cero.

| ID | Salida | Regla inicial | Estado enviado al generador original |
|---|---|---|---|
| 0 | reposo | Sonrisa, mandíbula y ceño < 0,20 | Punto medio |
| 1 | sonrisa | Promedio de sonrisa izquierda/derecha ≥ 0,45 y ceño < 0,35 | Abierta |
| 2 | boca_abierta | Mandíbula ≥ 0,45, sonrisa < 0,30 y ceño < 0,35 | Más abierta |
| 3 | ceno_fruncido | Mínimo de ambas cejas ≥ 0,35, sonrisa y mandíbula < 0,30 | Cerrada |

La sonrisa tiene prioridad cuando también abre la boca. Las mezclas que no cumplan una regla quedan sin confirmar. La ausencia de rostro reinicia confirmación e invalida generaciones pendientes. Los umbrales son iniciales y no se han seleccionado con validación del equipo. Hablar puede abrir la mandíbula y activar boca abierta; comprobarlo con participantes. Ajustar reposo no garantiza precisión ni reemplaza validación.

Se conservan hasta ocho muestras por segundo y tres decisiones consecutivas. La medición mostrada incluye preparación e inferencia CPU; excluye cámara, IPC, confirmación y carga del modelo. El trabajo pesado permanece en un proceso separado; pausa, reanudación y cierre conservan el ciclo original de la aplicación.

## Generación y alcance

No se modifica `floral.py`, `floral_worker.py`, `requirements-floral.txt` ni el notebook floral. La generación usa el entorno DirectML original, activado con `BLOOMFACE_ENABLE_LOCAL_GENERATOR=1` y preparado bajo `BLOOMFACE_FLORAL_RUNTIME`; de lo contrario aparece desactivada. MediaPipe puede comprobarse independientemente. No se agregan flores estáticas ni simulación.

El notebook histórico LibreFace se conserva como antecedente, sin importarse ni ejecutarse desde la aplicación. La carpeta anterior en Trabajo pdi conserva su historial y archivos; no es la versión exclusiva de esta rama.

Las pruebas de reglas usan señales controladas y dobles del SDK. La prueba real del modelo confirma carga y ausencia de rostro, no precisión de gestos. Se deben medir matriz de confusión, F1 macro, recall, rechazos y latencia con personas/sesiones reservadas y comprobar habla y mezclas. El spec incluye los recursos de MediaPipe; el ejecutable requiere construcción y prueba en Windows y la generación mantiene su Python externo original.

Comprobación del 22 de noviembre de 2026: pasaron 23 pruebas automáticas. Incluyen la carga del bundle y SDK reales en un proceso hijo, inferencia sobre un fotograma negro sin rostro, comando de ajuste de reposo y cierre limpio del proceso. Se comprobaron las cuatro solicitudes florales con señales controladas de la interfaz, pausa/reanudación y la ausencia de selector de modelos. `preparar_mediapipe.py --check-only` también completó carga real y `pip check` en el Python disponible de desarrollo. No se utilizó la webcam ni se midió precisión con participantes. Los archivos del generador, cámara y notebooks originales se compararon byte por byte con la base y permanecen iguales.

Fuentes: https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker/python y https://pypi.org/project/mediapipe/ .
