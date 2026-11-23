# Referencias conceptuales y técnicas

## Planteamiento del equipo

Ortiz González, C., Escobar Sánchez, J. A. y Romero Rada, J. D. (2026). *BloomFace Interpretación visual de la expresión facial mediante flores. Propuesta del proyecto final*. Universidad Autónoma de Occidente. [Documento original conservado](antecedentes/Propuesta_original_BloomFace.docx).

Este documento aporta el marco del macroproyecto y la problemática. Su arquitectura de CNN y sus fases de entrenamiento corresponden a la propuesta inicial; la documentación actual describe la implementación posterior.

## Fundamento artístico y alcance interpretativo

Achituv, R. y Utterback, C. (s. f.). *Text Rain*. Documentación de la instalación. [Sitio de Camille Utterback](https://camilleutterback.com/projects/text-rain/). Referencia de interacción entre movimientos corporales y respuesta visual digital.

Barrett, L. F., Adolphs, R., Marsella, S., Martinez, A. M. y Pollak, S. D. (2019). Emotional Expressions Reconsidered: Challenges to Inferring Emotion From Human Facial Movements. *Psychological Science in the Public Interest, 20*(1), 1–68. [DOI](https://doi.org/10.1177/1529100619832930). [Texto completo de los autores en PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6640856/). Sustenta la delimitación de gestos observables frente a interpretaciones emocionales dependientes del contexto.

## Reconocimiento y procesamiento de imágenes

Google. (s. f.). *MediaPipe Face Landmarker*. [Documentación oficial](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker?tab=Python). Describe detección de landmarks y coeficientes de expresión mediante modelos de aprendizaje automático.

OpenCV. (s. f.). *Structural Analysis and Shape Descriptors*. [Documentación de componentes conectados](https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html). Referencia de `connectedComponentsWithStats`, usado en el indicador de pétalos.

## Generación y ejecución local

Hugging Face. (s. f.). *ControlNet*. [Diffusers 0.32.2](https://huggingface.co/docs/diffusers/v0.32.2/api/pipelines/controlnet). Describe el condicionamiento espacial de la generación mediante imágenes de control.

Stable Diffusion. (s. f.). *Stable Diffusion v1 5*. [Repositorio de pesos y ficha del modelo](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5).

lllyasviel. (s. f.). *ControlNet v1 1 Scribble SD1 5*. [Repositorio del modelo](https://huggingface.co/lllyasviel/control_v11p_sd15_scribble).

Latent Consistency. (s. f.). *LCM LoRA SDv1 5*. [Repositorio del adaptador](https://huggingface.co/latent-consistency/lcm-lora-sdv1-5).

Microsoft. (s. f.). *Enable PyTorch with DirectML on Windows*. [Documentación oficial](https://learn.microsoft.com/en-us/windows/ai/directml/pytorch-windows).

Las versiones efectivas se fijan en los archivos de requisitos. La preparación floral registra las revisiones de los recursos descargados. Los enlaces conceptuales se contrastaron el 23 de noviembre de 2026; los resultados propios se atribuyen a los protocolos descritos en la documentación, no a estas fuentes generales.
