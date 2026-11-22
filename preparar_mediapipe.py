"""Prepara sólo el reconocimiento MediaPipe y la interfaz; no altera el generador floral."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from importlib.metadata import version, PackageNotFoundError

ROOT = Path(__file__).resolve().parent
LOCAL = ROOT / ".venv/Scripts/python.exe"
SMOKE = r"""
import json
from importlib.metadata import version
from PIL import Image
from bloomface.classifier import GestureClassifier
from bloomface.app import BloomFaceWindow
c = GestureClassifier()
try:
    r = c.diagnose(Image.new('RGB', (256, 256), 'black'))
    assert not r['face_detected'] and r['gesture'] is None
    assert len(r['scores']) == 4
finally:
    c.close()
print(json.dumps({n:version(n) for n in ['mediapipe','PySide6','opencv-contrib-python','numpy','Pillow']}))
"""


def requirements_satisfied():
    from pip._vendor.packaging.requirements import Requirement
    for text in (ROOT / 'requirements.txt').read_text(encoding='utf-8').splitlines():
        if not text.strip() or text.lstrip().startswith('#'):
            continue
        r = Requirement(text)
        try:
            if not r.specifier.contains(version(r.name), prereleases=True):
                return False
        except PackageNotFoundError:
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true', help='Comprueba el Python actual sin crear ni instalar entornos.')
    args = parser.parse_args()
    if not (3, 10) <= sys.version_info[:2] <= (3, 13) or sys.maxsize <= 2**32:
        raise RuntimeError('Usa Python de 64 bits 3.10 a 3.13; se recomienda 3.12.')
    if not args.check_only and Path(sys.prefix).resolve() != (ROOT / '.venv').resolve():
        if not LOCAL.is_file():
            subprocess.run([sys.executable, '-m', 'venv', str(ROOT / '.venv')], check=True)
        return subprocess.call([str(LOCAL), str(Path(__file__).resolve())], cwd=ROOT)
    output = ROOT / 'output'
    output.mkdir(exist_ok=True)
    state = {'preparado': False, 'recognizer': 'MediaPipe Face Landmarker', 'python': sys.executable}
    (output / 'estado_mediapipe.json').write_text(json.dumps(state), encoding='utf-8')
    with (output / 'preparacion_mediapipe.log').open('w', encoding='utf-8') as log:
        def run(command):
            env = dict(os.environ, PYTHONUTF8='1', PYTHONUNBUFFERED='1')
            with subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True, encoding='utf-8', errors='replace') as process:
                lines = []
                for line in process.stdout:
                    print(line, end='', flush=True)
                    log.write(line)
                    log.flush()
                    lines.append(line)
                if process.wait():
                    raise RuntimeError('Falló la preparación. Revisa output/preparacion_mediapipe.log.')
                return ''.join(lines)
        if not requirements_satisfied():
            if args.check_only:
                raise RuntimeError('El Python actual no satisface requirements.txt.')
            run([sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check', '--prefer-binary',
                 '--retries', '1', '--timeout', '20', '-r', str(ROOT / 'requirements.txt')])
        from bloomface.mediapipe_assets import ensure_model
        ensure_model(check_only=args.check_only)
        result = run([sys.executable, '-c', SMOKE])
        run([sys.executable, '-m', 'pip', 'check'])
        state.update(preparado=True, versiones=json.loads(result.strip().splitlines()[-1]),
                     alcance='Carga real del modelo e imagen sin rostro; no mide precisión ni prueba webcam.')
        (output / 'estado_mediapipe.json').write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8')
    print('MediaPipe preparado. Abre la cámara e inicia reconocimiento en la aplicación.', flush=True)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
