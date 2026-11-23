# Instalación y ejecución reproducible

## Requisitos

Windows x64, webcam para la experiencia en vivo, espacio para entornos y varios GB de modelos y memoria disponible para la difusión. La bitácora registra aproximadamente 8,1 GiB de pico del proceso floral en sus pruebas CPU; es una medición histórica de ese equipo, no un mínimo garantizado. La GPU necesita controladores compatibles con DirectML; CPU queda como respaldo. No se promete ejecución en todos los PC ni la misma latencia.

Para el notebook se necesita VS Code con soporte Python/Jupyter y un kernel local funcional. Si aparece «requires the ipykernel package», acepta **Install**. Ninguna celda puede ejecutar su preparación antes de existir un kernel. El entorno de la aplicación se prepara después, de forma independiente.

## A. Ejecutar esta carpeta de código con Run All

1. Abre la carpeta completa de esta copia en VS Code.
2. Abre `BloomFace_Instalar_y_Probar.ipynb` y usa **Run All / Ejecutar todo**.
3. La primera celda busca el proyecto a partir de la carpeta abierta y sus padres. Obtiene Python 3.12 x64 si el kernel usa otra versión. Crea `.venv/` para la interfaz y reconocimiento.
4. `preparar_mediapipe.py` instala dependencias y comprueba el modelo facial con una imagen sin rostro.
5. `preparar_floral.py` crea `floral_runtime/venv/`, instala PyTorch CPU + DirectML y el conjunto de difusión. Descarga configuraciones y pesos de los tres repositorios públicos si faltan.
6. La celda de apertura usa el Python local y la carpeta del proyecto como directorio de ejecución. No requiere escribir comandos ni guardar una ruta personal.

El entorno de reconocimiento usa NumPy compatible con MediaPipe; el entorno floral utiliza NumPy anterior a 2 y las versiones de difusión fijadas. Se mantienen separados para evitar conflictos. La preparación no abre la webcam ni prueba precisión facial. La primera carga de difusión ocurre al iniciar el reconocimiento.

Tras una preparación correcta, los archivos locales permiten inferencia sin conexión. La adquisición inicial de dependencias y modelos necesita Internet. Volver a ejecutar reutiliza los archivos y verifica importaciones, versiones y presencia de recursos; una consulta de instalación puede requerir red si falta alguna dependencia.

## B. Usar un portátil completo

Si el equipo entrega un ZIP portátil, extrae **toda la carpeta**, no solo el ejecutable, y abre `BloomFace.exe`. El portátil preparado por `empaquetar_portatil.py` incluye la interfaz y un Python floral aislado con pesos; no requiere VS Code ni instalar Python para usarlo.

Esta copia de revisión contiene código y documentación, no un ZIP ejecutable reconstruido. La bitácora describe compilaciones anteriores, pero esas carpetas `dist/` no estaban en el material copiado. Antes de entregar al profesor, el equipo debe construir o proporcionar el paquete correcto, verificarlo en otro Windows y publicar su enlace real con permisos de lectura.

## C. Desarrollo y construcción del portátil

Desde la raíz del proyecto, después de preparar con el notebook:

```powershell
.\.venv\Scripts\python.exe -m bloomface
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe preparar_floral.py --check-only
```

Para construir, instala PyInstaller en el entorno de interfaz y ejecuta:

```powershell
.\.venv\Scripts\python.exe -m pip install PyInstaller
.\.venv\Scripts\python.exe empaquetar_portatil.py --floral-runtime ".\floral_runtime" --zip
```

El script escribe una carpeta fechada en `dist/`, copia el entorno floral y verifica sus importaciones. La especificación incluye logo, dos tipografías activas, modelo facial, notebook y worker floral. La corrección de búsqueda de DLL registrada en el merge se conserva. Una compilación exitosa no sustituye probar el ejecutable en un Windows limpio.

## Diagnóstico

| Síntoma | Qué comprobar |
|---|---|
| Falta ipykernel | Instalarlo en el kernel seleccionado desde el aviso de VS Code |
| No se encuentra el proyecto | Abrir la carpeta completa y reiniciar el kernel si conservaba la ubicación de otra copia |
| No module named bloomface al usar terminal | Ejecutar desde la raíz del proyecto; el notebook ya fija ese directorio |
| Fallo de descarga | Internet, espacio y mensaje de error; reejecutar la preparación, que reutiliza archivos completos |
| Faltan archivos florales | Ejecutar la primera celda completa; no copiar solo `BloomFace.exe` |
| Primera imagen tarda | Carga inicial del modelo más inferencia; revisar estado GPU/CPU y memoria disponible |
| No se confirma gesto | Encuadre, luz, referencia de reposo, mezcla de movimientos y tres segundos continuos |
| Pausa tras mostrar flor | Es el final normal de ronda; usar Iniciar para la siguiente |

Los registros de preparación facial y aplicación se escriben en `output/`. El entorno floral guarda `preparacion.json` y `procedencia_modelos.json` en `floral_runtime/`. No compartas un JSON de reposo personal como calibración universal.
