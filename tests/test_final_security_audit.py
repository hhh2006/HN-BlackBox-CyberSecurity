from pathlib import Path
import json


def test_python_source_compiles_and_no_runtime_todos_in_core():
    root = Path(__file__).resolve().parents[1]
    offenders = []
    for path in root.rglob('*.py'):
        if any(part in {'__pycache__', '.git'} for part in path.parts):
            continue
        text = path.read_text(encoding='utf-8', errors='ignore')
        for marker in ('TODO', 'FIXME', 'NotImplemented'):
            if marker in text and 'docs' not in path.parts and 'tests' not in path.parts and path.name != 'security_audit.py':
                offenders.append((str(path.relative_to(root)), marker))
    # Historical documentation and deliberate exception handlers are allowed;
    # production code should not contain unfinished-work markers.
    assert not offenders


def test_cryptography_engine_manifest_is_stable():
    """The audit harness records the engine inventory without editing it."""
    root = Path(__file__).resolve().parents[1] / 'core' / 'cryptography'
    files = sorted(str(p.relative_to(root)) for p in root.rglob('*.py') if '__pycache__' not in p.parts)
    assert 'modern/aes_cipher.py' in files
    assert 'modern/des.py' in files
    assert 'modern/secure_rsa.py' in files
    assert 'modern/rsa.py' in files
    assert 'modern/hashing.py' in files
    assert 'steganography/steganography.py' in files
    assert 'classical/required/caesar.py' in files
    assert 'classical/required/keyed_transposition.py' in files
    assert 'classical/required/double_transposition.py' in files
    assert 'classical/additional/playfair.py' in files
    assert len(files) >= 15


def test_renderer_is_dependency_pinned_and_local():
    root = Path(__file__).resolve().parents[1]
    pkg = json.loads((root / 'renderer' / 'package.json').read_text(encoding='utf-8'))
    for name in ('three', 'gsap', 'pixi.js', '@tsparticles/engine', '@tsparticles/slim'):
        assert isinstance(pkg['dependencies'][name], str)
        assert not pkg['dependencies'][name].startswith('^')
        assert not pkg['dependencies'][name].startswith('~')


def test_cryptanalysis_legacy_rank_api_remains_compatible():
    from core.cryptanalysis import cryptanalysis
    rows = cryptanalysis.caesar_rank('KHOOR ZRUOG')
    assert len(rows) == 26
    assert all(len(row) == 3 for row in rows)
    assert any(key == 3 and plain == 'HELLO WORLD' for _score, key, plain in rows)
