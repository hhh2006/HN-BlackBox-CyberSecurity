from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gpu_surface_is_autonomous_and_pointer_independent():
    js = (ROOT / 'renderer/src/main.js').read_text()
    css = (ROOT / 'renderer/src/styles.css').read_text()
    assert 'requestAnimationFrame(frame)' in js
    assert 'setInterval' in js
    assert 'autonomousTelemetryBus' in js
    assert 'autonomousHexStreamBus' in js
    assert 'autoSweep' in js
    assert 'autoLens' in js
    assert 'pointer-events:none' in css
    assert 'panelHeartbeat' in css
    assert 'fieldScan' in css
    assert 'gridDrift' in css
    assert 'panelLaser' in css


def test_crypto_decks_keep_real_controls_and_instant_clipboard():
    html = (ROOT / 'renderer/index.html').read_text()
    app = (ROOT / 'gui/app.py').read_text()
    assert 'crypto-exec' in html
    assert 'copy-encrypted' in html
    assert 'copy-extracted' in html
    assert 'open_crypto_analyzer' in app
    assert 'frequency_analysis.analyze' in app
    assert 'self.clipboard_clear()' in app


def test_crypto_implementations_remain_canonical():
    required = [
        'caesar.py','additive.py','multiplicative.py','affine.py','vigenere.py',
        'autokey.py','rail_fence.py','keyed_transposition.py','double_transposition.py'
    ]
    for name in required:
        assert (ROOT/'core/cryptography/classical/required'/name).exists()
    for name in ['aes_cipher.py','des.py','rsa.py','secure_rsa.py','hashing.py']:
        assert (ROOT/'core/cryptography/modern'/name).exists()
    assert (ROOT/'core/cryptography/steganography/steganography.py').exists()
