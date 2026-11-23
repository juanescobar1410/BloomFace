# -*- mode: python ; coding: utf-8 -*-


from pathlib import Path
from PyInstaller.utils.hooks import collect_all

mp_datas, mp_binaries, mp_hiddenimports = collect_all('mediapipe')
model = Path('bloomface/models/mediapipe/face_landmarker.task')
logo = Path('bloomface/assets/brand/BloomFace_Logo.png')
if not logo.is_file():
    raise SystemExit('Falta el logo: ' + str(logo))
if not model.is_file():
    raise SystemExit('Prepara MediaPipe con el notebook: falta ' + str(model))

a = Analysis(
    ['bloomface/__main__.py'],
    pathex=['.'],
    binaries=mp_binaries,
    datas=[
        (str(logo), 'bloomface/assets/brand'),
        ('agrandir-font-family', 'agrandir-font-family'),
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
# Qt uses the unversioned ICU ABI provided by Windows. A third-party DLL with
# the same filename can otherwise override it in the frozen application.
a.binaries = [entry for entry in a.binaries if entry[0].lower() not in {"icuuc.dll", "icuin.dll"}]

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
