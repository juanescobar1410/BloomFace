# -*- mode: python ; coding: utf-8 -*-


from pathlib import Path
from PyInstaller.utils.hooks import collect_all

mp_datas, mp_binaries, mp_hiddenimports = collect_all('mediapipe')
model = Path('bloomface/models/mediapipe/face_landmarker.task')
if not model.is_file():
    raise SystemExit('Prepara MediaPipe con el notebook: falta ' + str(model))

a = Analysis(
    ['bloomface/__main__.py'],
    pathex=['.'],
    binaries=mp_binaries,
    datas=[
        ('notebooks/BloomFace_Generacion_Floral.ipynb', 'notebooks'),
        ('bloomface/floral_worker.py', 'bloomface'),
        (str(model), 'bloomface/models/mediapipe'),
    ] + mp_datas,
    hiddenimports=mp_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BloomFace',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BloomFace',
)
