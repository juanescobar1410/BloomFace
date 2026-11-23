"""Prepara el entorno floral que consume la versión DirectML/CPU de BloomFace."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
os.environ.setdefault('HF_HUB_DISABLE_XET', '1')
os.environ.setdefault('HF_HUB_ETAG_TIMEOUT', '30')
os.environ.setdefault('HF_HUB_DOWNLOAD_TIMEOUT', '60')
FILES = {
    'sd15': ('stable-diffusion-v1-5/stable-diffusion-v1-5', [
        'model_index.json', 'scheduler/scheduler_config.json',
        'tokenizer/merges.txt', 'tokenizer/vocab.json', 'tokenizer/tokenizer_config.json',
        'tokenizer/special_tokens_map.json', 'feature_extractor/preprocessor_config.json',
        'text_encoder/config.json', 'text_encoder/model.fp16.safetensors',
        'safety_checker/config.json', 'safety_checker/model.fp16.safetensors',
        'unet/config.json', 'unet/diffusion_pytorch_model.fp16.safetensors',
        'vae/config.json', 'vae/diffusion_pytorch_model.fp16.safetensors']),
    'scribble': ('lllyasviel/control_v11p_sd15_scribble', [
        'config.json', 'diffusion_pytorch_model.fp16.safetensors']),
    'lcm': ('latent-consistency/lcm-lora-sdv1-5', ['pytorch_lora_weights.safetensors']),
}


def missing_weights(runtime):
    return [f'{folder}/{name}' for folder, (_, names) in FILES.items() for name in names
            if not (runtime / 'weights' / folder / name).is_file()
            or (runtime / 'weights' / folder / name).stat().st_size == 0]


def download_weights(runtime):
    from huggingface_hub import HfApi, snapshot_download
    records = {}
    for folder, (repo, names) in FILES.items():
        if not any(p.startswith(folder + '/') for p in missing_weights(runtime)):
            continue
        info = HfApi().model_info(repo, token=False)
        print('Descargando recursos públicos:', repo, flush=True)
        snapshot_download(repo, revision=info.sha, local_dir=runtime / 'weights' / folder,
                          allow_patterns=names, token=False, max_workers=1)
        records[folder] = {'repo': repo, 'revision': info.sha, 'files': names}
    missing = missing_weights(runtime)
    if missing:
        raise RuntimeError('Faltan recursos tras la descarga: ' + ', '.join(missing))
    manifest = runtime / 'procedencia_modelos.json'
    previous = json.loads(manifest.read_text(encoding='utf-8')) if manifest.is_file() else {}
    previous.update(records)
    manifest.write_text(json.dumps(previous, ensure_ascii=False, indent=2), encoding='utf-8')


def check_environment():
    from importlib.metadata import version
    from pip._vendor.packaging.requirements import Requirement
    for line in (ROOT / 'requirements-floral.txt').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith(('#', '--')):
            continue
        req = Requirement(line)
        if not req.specifier.contains(version(req.name), prereleases=True):
            raise RuntimeError('Versión incompatible: ' + req.name)
    import torch
    from diffusers import ControlNetModel, LCMScheduler, StableDiffusionPipeline
    import peft
    assert torch.version.cuda is None, 'El entorno de esta versión utiliza PyTorch CPU + DirectML.'
    assert importlib.util.find_spec('torch_directml') is not None
    assert importlib.util.find_spec('torch_directml_native') is not None
    print('Dependencias florales comprobadas: CPU + DirectML.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inside', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    runtime = ROOT / 'floral_runtime'
    python = runtime / 'venv/Scripts/python.exe'
    env = dict(os.environ, PYTHONUTF8='1', PYTHONUNBUFFERED='1')
    if not args.inside:
        if os.name != 'nt' or sys.version_info[:2] != (3, 12) or sys.maxsize <= 2**32:
            raise RuntimeError('El preparador requiere Windows x64 y Python 3.12. Usa la primera celda del notebook para obtenerlo.')
        if not python.is_file():
            if args.check_only:
                raise RuntimeError('Falta el entorno floral; ejecuta la preparación completa.')
            subprocess.run([sys.executable, '-m', 'venv', str(runtime / 'venv')], check=True)
        command = [str(python), '-B', str(Path(__file__)), '--inside']
        if args.check_only:
            command.append('--check-only')
        subprocess.run(command, cwd=ROOT, env=env, check=True)
        return
    try:
        check_environment()
    except (ImportError, AssertionError, RuntimeError):
        if args.check_only:
            raise
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check',
                        '--prefer-binary', '--no-compile', '--timeout', '60', '--retries', '2',
                        '-r', str(ROOT / 'requirements-floral.txt')], cwd=ROOT, env=env, check=True)
        check_environment()
    if missing_weights(runtime):
        if args.check_only:
            raise RuntimeError('Faltan pesos florales: ' + ', '.join(missing_weights(runtime)))
        download_weights(runtime)
    subprocess.run([sys.executable, '-m', 'pip', 'check'], check=True, env=env)
    report = {'preparado': True, 'runtime': str(runtime), 'backend': 'DirectML con respaldo en CPU',
              'alcance': 'Importación, versiones y presencia de recursos. No mide precisión ni genera una imagen.'}
    (runtime / 'preparacion.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Generador preparado. El primer inicio cargará los modelos; puede tardar.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print('Preparación floral incompleta:', error, file=sys.stderr)
        raise SystemExit(1)
