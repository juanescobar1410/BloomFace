import ast
import base64
from io import BytesIO
import json
from pathlib import Path
from random import SystemRandom
import sys
import time

from diffusers import ControlNetModel, LCMScheduler, StableDiffusionPipeline
from diffusers.models.attention_processor import AttnProcessor
from PIL import Image, ImageDraw
import torch
import torch_directml


def read_configuration(path):
    names = {"contornos", "contornos_nuevos", "formas", "formas_nuevas", "estilo", "etapa_por_expresion"}
    book = json.loads(path.read_text(encoding="utf-8"))
    values = {}
    for cell in book["cells"]:
        source = "".join(cell["source"])
        if not source.startswith("contornos = {"):
            continue
        for node in ast.parse(source).body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in names:
                        values[target.id] = ast.literal_eval(node.value)
    if set(values) != names:
        raise ValueError("Faltan prompts o guías en el cuaderno floral.")
    return values


class FloralGenerator:
    def __init__(self, notebook, weights):
        torch.set_num_threads(4)
        self.device = next(
            (torch_directml.device(index)
             for index in range(torch_directml.device_count())
             if "RX 6600 XT" in torch_directml.device_name(index)),
            None,
        )
        if self.device is None:
            raise RuntimeError("PyTorch DirectML no detectó la Radeon RX 6600 XT.")
        self.dtype = torch.float16
        self.base = StableDiffusionPipeline.from_pretrained(
            str(weights / "sd15"), torch_dtype=self.dtype, variant="fp16",
            use_safetensors=True, local_files_only=True,
        )
        if self.base.safety_checker is None:
            raise RuntimeError("Falta el filtro de seguridad del modelo.")
        self.base.load_lora_weights(
            str(weights / "lcm"), weight_name="pytorch_lora_weights.safetensors",
            adapter_name="lcm_rapido", local_files_only=True,
        )
        self.base.fuse_lora(adapter_names=["lcm_rapido"], safe_fusing=True)
        self.base.unload_lora_weights()
        self.control = ControlNetModel.from_pretrained(
            str(weights / "scribble"), torch_dtype=self.dtype, variant="fp16",
            use_safetensors=True, local_files_only=True,
        )
        self.base.text_encoder.float()
        self.base.safety_checker.float()
        self.vae = self.base.vae
        self.unet = self.base.unet
        for model in (self.vae, self.unet, self.control):
            model.set_attn_processor(AttnProcessor())
            model.to(device=self.device, dtype=self.dtype)
        self.unet.set_attention_slice("auto")
        self.control.set_attention_slice("auto")
        self.scheduler = LCMScheduler.from_config(self.base.scheduler.config)
        values = read_configuration(notebook)
        self.stages = values["etapa_por_expresion"]
        contours = {**values["contornos"], **values["contornos_nuevos"]}
        descriptions = {**values["formas"], **values["formas_nuevas"]}
        self.conditions = {}
        with torch.no_grad():
            for stage, contour in contours.items():
                guide = Image.new("RGB", (512, 512), "black")
                drawing = ImageDraw.Draw(guide)
                drawing.line(contour, fill="white", width=5, joint="curve")
                drawing.line([(256, 270), (254, 335), (256, 410)], fill="white", width=5)
                # ControlNet recibe RGB [0, 1].
                guide_array = self.base.image_processor.pil_to_numpy(guide)
                guide_tensor = self.base.image_processor.numpy_to_pt(guide_array)
                prompt, _ = self.base.encode_prompt(
                    f'{descriptions[stage]}, {values["estilo"]}', device=torch.device("cpu"),
                    num_images_per_prompt=1, do_classifier_free_guidance=False,
                )
                self.conditions[stage] = tuple(
                    tensor.to(device=self.device, dtype=self.dtype) for tensor in (prompt, guide_tensor)
                )

    @torch.no_grad()
    def attempt(self, stage, seed):
        prompt, guide = self.conditions[stage]
        generator = torch.Generator(device="cpu").manual_seed(seed)
        self.scheduler.set_timesteps(4, device="cpu")
        latents = torch.randn((1, 4, 64, 64), generator=generator) * self.scheduler.init_noise_sigma
        for timestep in self.scheduler.timesteps:
            latent_input = self.scheduler.scale_model_input(latents, timestep).to(device=self.device, dtype=self.dtype)
            timestep_device = timestep.to(device=self.device)
            down, middle = self.control(
                latent_input, timestep_device, encoder_hidden_states=prompt,
                controlnet_cond=guide, conditioning_scale=0.9, return_dict=False,
            )
            noise = self.unet(
                latent_input, timestep_device, encoder_hidden_states=prompt,
                down_block_additional_residuals=down, mid_block_additional_residual=middle,
                return_dict=False,
            )[0]
            latents = self.scheduler.step(noise.cpu().float(), timestep, latents, generator=generator).prev_sample
        latent = latents.to(device=self.device, dtype=self.dtype) / self.vae.config.scaling_factor
        decoded = self.vae.decode(latent, return_dict=False)[0].cpu().float()
        decoded, flagged = self.base.run_safety_checker(decoded, torch.device("cpu"), torch.float32)
        if flagged[0]:
            return None
        image = self.base.image_processor.postprocess(decoded, output_type="pil")[0]
        return image if image.getbbox() is not None else None

    def generate(self, gesture):
        stage = self.stages[gesture]
        for seed in SystemRandom().sample(range(2**32), 2):
            image = self.attempt(stage, seed)
            if image is not None:
                return image
        return None


def send(message):
    print(json.dumps(message), flush=True)


def main():
    try:
        generator = FloralGenerator(Path(sys.argv[1]), Path(sys.argv[2]))
    except Exception as error:
        send({"error": str(error)})
        return
    send({"ready": True})
    for line in sys.stdin:
        request = json.loads(line)
        response = {"id": request["id"]}
        started = time.perf_counter()
        try:
            image = generator.generate(request["gesture"])
            if image is not None:
                buffer = BytesIO()
                image.save(buffer, format="PNG")
                response["image"] = base64.b64encode(buffer.getvalue()).decode("ascii")
            else:
                response["error"] = "No se obtuvo una acuarela utilizable."
        except Exception as error:
            response["error"] = str(error)
        response["seconds"] = time.perf_counter() - started
        send(response)


if __name__ == "__main__":
    main()
