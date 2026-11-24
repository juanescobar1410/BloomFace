# Verificación reproducible

## Pruebas automatizadas

Después de preparar el reconocimiento:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

La suite cubre reglas, confirmación temporal, métricas con rechazos, adaptador facial, descarga simulada, IPC y conexión de la UI. La prueba facial real usa una imagen negra y se omite si no están instalados el SDK y el bundle. Que no haya rostro en esa imagen no evalúa reconocimiento de gestos con personas.

Las pruebas de UI suministran señales; las de recuperación simulan fallos de proceso. Las nuevas pruebas de preparación usan entornos temporales y dobles para comprobar que el notebook invoca ambos preparadores desde otra carpeta y que un fallo no deja un estado de éxito. No descargan varios GB en cada corrida.

## Revisión manual de la copia

| Caso | Acción | Resultado esperado |
|---|---|---|
| Instalación inicial | Run All desde una carpeta sin entornos | Se preparan interfaz, reconocimiento y generación; se abre BloomFace |
| Reutilización | Repetir tras cerrar la app | Se reutilizan modelos y entornos completos |
| Bienvenida e instrucciones | INICIAR y flecha | Aparecen instrucciones y vista principal |
| Cuatro gestos | Mantener cada uno tres segundos en rondas distintas | Se confirma el gesto y se solicita su etapa |
| Interrupción | Cambiar o perder rostro antes de tres segundos | Se reinicia el borde y no se confirma |
| Una flor por ronda | Cambiar de gesto durante generación | Se conserva la solicitud de la ronda |
| Resultado | Esperar la acuarela | Se pausa y el mismo Iniciar ofrece otra ronda |
| Pausa manual | Pausar y Reanudar | Composición conservada; nuevo intento de reconocimiento |
| Fallo de GPU | Entorno sin DirectML utilizable o fallo controlado | Se intenta CPU y se conserva la solicitud vigente |
| Rechazo de generación | Resultado no aceptado | Se conserva imagen previa y se permite otra ronda |
| Cierre | Cerrar durante captura / generación | Se liberan cámara y procesos |

La prueba sin GPU puede ser costosa. No es necesario provocar un fallo del controlador; se puede ensayar el controlador con dobles como hace la suite. La cámara física no se activa durante la generación de capturas documentales.

## Evaluación exploratoria realizada

El equipo registró cinco participantes y 20 intentos, uno por gesto y persona. Los indicadores funcionales y los tiempos separados por dispositivo y primera carga se presentan en [resultados](resultados.md#evaluación-exploratoria-con-cinco-participantes); los valores consultados se conservan en una [instantánea local](evidencias/validacion_participantes_2026-11-23.json). Esta prueba no ejecuta ni sustituye todos los casos de la lista manual anterior. Quedan pendientes la corrección temporal de J18, la identificación del backend de P4 y el registro de condiciones y evidencias.

## Ampliación de la evaluación con participantes

Separar personas y sesiones de evaluación del ajuste de umbrales. Registrar por intento gesto real, decisión o rechazo, luz, distancia, sesión y tiempo. Incluir habla, movimientos mixtos, cambios rápidos y ausencia de rostro. Obtener matriz de confusión con rechazo, recall, F1 macro y exactitud con rechazo; informar número de personas e intentos y condiciones.

Para las imágenes, registrar etapa solicitada, semilla, resolución, tiempo, reintentos y aceptación visual. Evaluar diferenciación entre etapas y coherencia estilística mediante un criterio explícito. Obtener autorización para conservar imágenes de participantes; el recorrido actual trabaja en memoria.
