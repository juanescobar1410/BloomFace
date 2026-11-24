# BloomFace

**Creación visual a partir de gestos faciales y composiciones florales.** Proyecto final de Procesamiento Digital de Imágenes de la Universidad Autónoma de Occidente, en el marco del macroproyecto **Análisis de la Expresión Humana en el Arte y la Cultura**.

BloomFace propone una experiencia artística local en la que la persona participa mediante movimientos visibles de su rostro. El sistema vincula esos gestos con etapas de apertura de una flor y genera una respuesta visual mediante modelos preentrenados.

**Autores:** Catalina Ortiz González, Juan Andrés Escobar Sánchez y Juan David Romero Rada.

![Pantalla de bienvenida de BloomFace](docs/evidencias/01_bienvenida.png)

## Qué hace

La aplicación de escritorio para Windows recibe la webcam, obtiene señales de movimiento con MediaPipe Face Landmarker y confirma un gesto tras tres segundos continuos. Stable Diffusion 1.5, ControlNet Scribble y LCM-LoRA generan una acuarela. Se toma **un gesto por ronda**; al mostrar la flor se pausa y el botón **Iniciar** permite otra ronda.

| Gesto | Etapa floral |
|---|---|
| Ceño fruncido | Cerrada |
| Reposo | Punto medio |
| Sonrisa | Abierta |
| Boca abierta | Más abierta |

## Abrir el proyecto

1. Abre **la carpeta completa del proyecto** en VS Code para evitar ejecutar otra copia del proyecto.
2. Abre `BloomFace_Instalar_y_Probar.ipynb`.
3. Selecciona un kernel Python local funcional. Si VS Code solicita `ipykernel`, acepta instalarlo. El notebook necesita ese kernel para ejecutar su primera celda.
4. Pulsa **Run All / Ejecutar todo** y espera a que termine la preparación. Obtendrá Python 3.12 si hace falta, instalará los dos entornos y descargará los modelos públicos. La primera vez requiere Internet y varios GB de disco.
5. En BloomFace pulsa **INICIAR → flecha → Iniciar**. Mantén un gesto tres segundos y espera la acuarela. Después pulsa **Iniciar** para otra flor.

Para reconocer los gestos, ubícate de frente a la cámara con iluminación estable y mantén visibles las cejas, los ojos y la boca. El cabello, las manos, las mascarillas y los accesorios que cubran esas zonas pueden dificultar la detección o provocar confusiones entre expresiones. Ajusta los objetos que obstruyan el rostro antes de iniciar y conserva el encuadre durante los tres segundos de confirmación.

Las siguientes ejecuciones reutilizan los recursos. DirectML intenta usar una GPU compatible; la aplicación recupera el gesto vigente en CPU si la GPU falla o supera el tiempo de espera. Una GPU dedicada compatible y con suficiente memoria suele ofrecer mejores tiempos de generación. BloomFace también puede utilizar gráficos integrados compatibles o recurrir a CPU, con tiempos que dependen del procesador, la memoria disponible y los controladores. En esos equipos la espera puede aumentar considerablemente.

La primera acuarela incluye la carga del modelo además de la generación de la imagen y puede tardar más que las siguientes. Espera a que finalice el indicador de carga. Los tiempos varían entre dispositivos. Consulta [instalación y solución de problemas](docs/instalacion.md).

## Documentación del proyecto

| Contenido solicitado | Documento |
|---|---|
| Problemática, justificación, objetivos y solución | [Descripción del proyecto](docs/proyecto.md) |
| Técnicas de PDI y visión computacional implementadas | [Correspondencia técnica](docs/metodologia.md#técnicas-de-procesamiento-de-imágenes-y-visión-computacional) |
| Fundamento artístico y fuentes técnicas | [Referencias](docs/referencias.md) |
| Componentes, conexiones y funcionamiento | [Arquitectura y diagramas](docs/arquitectura.md) |
| Etapas de desarrollo, técnicas y modelos | [Metodología e implementación](docs/metodologia.md) |
| Datos, recursos, procedencia y acceso | [Datos y modelos](docs/datos.md) |
| Prototipo, funciones, uso y evidencias | [Interfaz y manual](docs/interfaz.md) |
| Cobertura de los requisitos de la imagen | [Lista de entrega](docs/entrega.md) |

## Ejecutable portátil y desarrollo

La carpeta de código **no incluye un `BloomFace.exe` ni un ZIP portátil**. Las instrucciones para usar un portátil completo o construirlo están en [instalación](docs/instalacion.md). Los recursos grandes quedan fuera del código fuente y los prepara el notebook.

El código se organiza en `bloomface/`, el cuaderno floral activo en `notebooks/` y las pruebas en `tests/`. Los experimentos anteriores y la bitácora original se conservan en [antecedentes](docs/antecedentes/README.md). Los pesos y entornos se generan en `.venv/`, `bloomface/models/` y `floral_runtime/`, excluidos de Git.
