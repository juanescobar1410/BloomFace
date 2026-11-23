import importlib.util
import json
import io
import os
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import preparar_notebook
import preparar_floral

ROOT = Path(__file__).resolve().parents[1]


class PreparationRevisionTests(unittest.TestCase):
    def test_console_with_limited_encoding_does_not_block_preparation(self):
        stream = io.BytesIO()
        console = io.TextIOWrapper(stream, encoding='ascii', write_through=True)
        try:
            with patch.object(sys, 'stdout', console):
                preparar_notebook.run([sys.executable, '-c', "print(chr(0x2192))"],
                                      ROOT, dict(os.environ, PYTHONUTF8='1'))
            self.assertIn(b'?', stream.getvalue())
        finally:
            console.detach()

    def test_notebook_locates_another_copy_and_calls_its_preparer(self):
        notebook = json.loads((ROOT / 'BloomFace_Instalar_y_Probar.ipynb').read_text(encoding='utf-8'))
        code = next(''.join(c['source']) for c in notebook['cells'] if c['cell_type'] == 'code')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / 'bloomface').mkdir()
            (root / 'bloomface/__main__.py').touch()
            (root / 'preparar_notebook.py').write_text(
                'def prepare(root):\n    (root / "called").touch()\n'
                '    return root / "python.exe", root / "output", {}, {"preparado": True}\n', encoding='utf-8')
            scope = {}
            with patch.object(Path, 'cwd', return_value=root):
                exec(compile(code, '<first-cell>', 'exec'), scope)
            self.assertTrue(scope['PREPARADO'])
            self.assertEqual(scope['PROYECTO'], root)
            self.assertTrue((root / 'called').is_file())

    def test_first_cell_does_not_claim_ready_on_preparation_failure(self):
        notebook = json.loads((ROOT / 'BloomFace_Instalar_y_Probar.ipynb').read_text(encoding='utf-8'))
        code = next(''.join(c['source']) for c in notebook['cells'] if c['cell_type'] == 'code')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / 'bloomface').mkdir()
            (root / 'bloomface/__main__.py').touch()
            (root / 'preparar_notebook.py').write_text('def prepare(root):\n    raise RuntimeError("download failed")\n', encoding='utf-8')
            scope = {}
            with patch.object(Path, 'cwd', return_value=root), self.assertRaisesRegex(RuntimeError, 'download failed'):
                exec(compile(code, '<first-cell>', 'exec'), scope)
            self.assertFalse(scope['PREPARADO'])

    def test_portable_preparer_invokes_face_then_floral_in_the_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'output').mkdir()
            (root / 'output/estado_mediapipe.json').write_text('{"preparado":true}', encoding='utf-8')
            with patch.object(preparar_notebook, 'supported_python', return_value=True), patch.object(preparar_notebook, 'run') as run:
                python, output, env, state = preparar_notebook.prepare(root)
            self.assertEqual(run.call_count, 2)
            self.assertEqual(Path(run.call_args_list[0].args[0][-1]), root.resolve() / 'preparar_mediapipe.py')
            self.assertEqual(run.call_args_list[1].args[0][-1], root.resolve() / 'preparar_floral.py')
            self.assertEqual(env['BLOOMFACE_FLORAL_RUNTIME'], str(root.resolve() / 'floral_runtime'))
            self.assertEqual(env['MPLBACKEND'], 'Agg')

    def test_incomplete_weights_are_not_declared_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = preparar_floral.missing_weights(root)
            self.assertIn('sd15/unet/diffusion_pytorch_model.fp16.safetensors', missing)
            for folder, (_, names) in preparar_floral.FILES.items():
                for name in names:
                    path = root / 'weights' / folder / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b'x')
            self.assertEqual(preparar_floral.missing_weights(root), [])
            (root / 'weights/lcm/pytorch_lora_weights.safetensors').write_bytes(b'')
            self.assertEqual(preparar_floral.missing_weights(root), ['lcm/pytorch_lora_weights.safetensors'])
