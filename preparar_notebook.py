"""Preparación portátil del notebook; usa sólo la biblioteca estándar al arrancar."""
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time


def supported_python(executable):
    try:
        result = subprocess.run(
            [str(executable), '-c',
             'import sys,struct; sys.exit(not ((3,10) <= sys.version_info[:2] <= (3,13) and struct.calcsize("P") == 8))'],
            capture_output=True, timeout=15,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def run(command, root, env):
    with subprocess.Popen([str(x) for x in command], cwd=root, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, encoding='utf-8', errors='replace') as process:
        for line in process.stdout:
            print(line, end='', flush=True)
        if process.wait():
            raise RuntimeError('La preparación no terminó. Revisa el mensaje anterior y vuelve a ejecutar la celda. Necesita Internet la primera vez.')


def prepare(root):
    if os.name != 'nt':
        raise RuntimeError('Ejecuta este notebook en Windows local para usar la webcam y la interfaz.')
    root = Path(root).resolve()
    output = root / 'output'
    output.mkdir(exist_ok=True)
    env = dict(os.environ, PYTHONUTF8='1', PYTHONUNBUFFERED='1')
    local = root / '.venv/Scripts/python.exe'
    print('Proyecto:', root, flush=True)
    if not supported_python(local):
        # Preserve any old or copied environment instead of overwriting its files.
        venv = root / '.venv'
        if venv.exists():
            backup = root / ('.venv-respaldo-' + str(time.time_ns()))
            venv.rename(backup)
            print('Entorno anterior conservado en:', backup.name, flush=True)
        if supported_python(sys.executable):
            print('Creando el entorno local con el Python disponible…', flush=True)
            run([sys.executable, '-m', 'venv', venv], root, env)
        else:
            # uv supplies Python 3.12 even if the notebook kernel is Python 3.15.
            # Keep its tools, cache and managed Python under this project.
            tools = output / 'bootstrap'
            uv = next(tools.rglob('uv.exe'), None) if tools.exists() else None
            if uv is None:
                print('Preparando uv desde PyPI para obtener Python 3.12…', flush=True)
                run([sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check',
                     '--only-binary=:all:', '--target', tools, 'uv>=0.9,<1'], root, env)
                uv = next(tools.rglob('uv.exe'), None)
                if uv is None:
                    raise RuntimeError('No se encontró uv.exe después de instalar uv.')
            env.update(UV_PYTHON_INSTALL_DIR=str(output / 'python'),
                       UV_CACHE_DIR=str(output / 'uv-cache'))
            print('Preparando Python 3.12 y el entorno local…', flush=True)
            run([uv, 'venv', '--python', '3.12', '--managed-python', '--seed', venv], root, env)
    if not supported_python(local):
        raise RuntimeError('No se pudo preparar un Python compatible para BloomFace.')
    # Run the existing installer in the app environment, never in the notebook kernel.
    run([local, root / 'preparar_mediapipe.py'], root, env)
    state = json.loads((output / 'estado_mediapipe.json').read_text(encoding='utf-8'))
    if not state.get('preparado'):
        raise RuntimeError('El modelo no completó la comprobación.')
    return local, output, env, state
