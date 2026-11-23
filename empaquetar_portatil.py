"""Construye la distribución portátil con un entorno floral local ya preparado."""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZIP_STORED, ZipFile


PROJECT = Path(__file__).resolve().parent


def read_floral_environment(runtime):
    python = runtime / "venv" / "Scripts" / "python.exe"
    if not python.is_file():
        raise SystemExit(f"Falta el Python del entorno floral: {python}")
    probe = """
import importlib.util, json, platform, sys, sysconfig
import torch
from diffusers import ControlNetModel, LCMScheduler, StableDiffusionPipeline
import peft
import PIL
assert sys.version_info[:2] == (3, 12) and platform.machine().upper() == "AMD64"
assert torch.version.cuda is None and torch.version.hip is None, "Se necesita PyTorch para CPU"
assert importlib.util.find_spec("torch_directml") is not None, "Falta el paquete DirectML"
assert importlib.util.find_spec("torch_directml_native") is not None, "Falta la extensión nativa DirectML"
print(json.dumps([sys.base_prefix, sysconfig.get_path("purelib")]))
"""
    return tuple(map(Path, json.loads(subprocess.check_output(
        [str(python), "-I", "-B", "-c", probe], text=True,
    ))))


def copy_floral_runtime(base_python, site_packages, weights, app):
    destination = app / "floral_runtime"
    python = destination / "python"
    python.mkdir(parents=True)
    for name in ("python.exe", "python3.dll", "python312.dll", "LICENSE.txt"):
        shutil.copyfile(base_python / name, python / name)
    for dll in base_python.glob("vcruntime*.dll"):
        shutil.copyfile(dll, python / dll.name)
    shutil.copyfile(app / "_internal" / "PySide6" / "MSVCP140.dll", python / "MSVCP140.dll")
    shutil.copytree(base_python / "DLLs", python / "DLLs", copy_function=shutil.copyfile)
    shutil.copytree(base_python / "Lib", python / "Lib", copy_function=shutil.copyfile,
                    ignore=shutil.ignore_patterns("site-packages", "__pycache__", "ensurepip",
                                                 "idlelib", "tkinter", "test"))
    shutil.copytree(site_packages, python / "Lib" / "site-packages", copy_function=shutil.copyfile,
                    ignore=shutil.ignore_patterns("__pycache__", "*.whl",
                                                 "pip", "pip-*.dist-info"))
    (python / "python312._pth").write_text(
        ".\nDLLs\nLib\nLib/site-packages\nimport site\n", encoding="ascii",
    )
    shutil.copytree(weights, destination / "weights", copy_function=shutil.copyfile)
    subprocess.run(
        [str(python / "python.exe"), "-I", "-B", "-c",
         "import importlib.util, pathlib, sys, torch; "
         "from diffusers import ControlNetModel, LCMScheduler, StableDiffusionPipeline; "
         "assert pathlib.Path(torch.__file__).is_relative_to(pathlib.Path(sys.executable).parent); "
         "assert importlib.util.find_spec('torch_directml') is not None; "
         "assert importlib.util.find_spec('torch_directml_native') is not None; "
         "assert (pathlib.Path(sys.executable).parent / 'Lib/site-packages/torch_directml/DirectML.dll').is_file(); "
         "assert torch.version.cuda is None and torch.version.hip is None; "
         "assert torch.ones(1).device.type == 'cpu'"],
        check=True, cwd=destination,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--floral-runtime", required=True, type=Path,
                        help="Carpeta con el entorno venv y los pesos locales.")
    parser.add_argument("--zip", action="store_true", help="Empaqueta también la carpeta en un ZIP.")
    args = parser.parse_args()
    runtime = args.floral_runtime.resolve()
    weights = runtime / "weights"
    for name in ("sd15/model_index.json", "scribble/config.json",
                 "lcm/pytorch_lora_weights.safetensors"):
        if not (weights / name).is_file():
            parser.error(f"Falta el archivo {weights / name}")

    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    base_python, site_packages = read_floral_environment(runtime)
    output = PROJECT / "dist" / f"BloomFace-Auto-{datetime.now():%Y%m%d-%H%M%S-%f}"
    build = PROJECT / "build" / output.name
    print(f"Generando carpeta portátil en {output}", flush=True)
    # Dependency analysis searches PATH for native libraries. Restrict it to
    # the build interpreter and Windows so other applications cannot supply DLLs.
    windows = Path(os.environ["SystemRoot"])
    build_environment = os.environ.copy()
    build_environment["PATH"] = os.pathsep.join(map(str, (
        Path(sys.executable).parent, Path(sys.base_prefix), windows / "System32", windows,
    )))
    subprocess.run(
        [sys.executable, "-I", "-m", "PyInstaller", "--clean", "--distpath", str(output),
         "--workpath", str(build), "BloomFace.spec"],
        check=True, cwd=PROJECT, env=build_environment,
    )
    app = output / "BloomFace"
    copy_floral_runtime(base_python, site_packages, weights, app)
    print(f"Ejecutable portátil: {app / 'BloomFace.exe'}", flush=True)
    if args.zip:
        archive_path = output / "BloomFace-Windows-x64-GPU-CPU.zip"
        with ZipFile(archive_path, "w", compression=ZIP_STORED) as archive:
            for file in app.rglob("*"):
                if file.is_file():
                    archive.write(file, file.relative_to(output))
        print(f"Archivo portátil: {archive_path}", flush=True)


if __name__ == "__main__":
    main()
