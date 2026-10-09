from pathlib import Path
from PIL import Image
from core.cryptography.classical.required import keyed_transposition
from core.cryptography.steganography import steganography as stego


def test_keyed_transposition_roundtrip():
    text = "THIS IS A SECRET MESSAGE"
    cipher = keyed_transposition.columnar_encrypt(text, "SECURITY")
    assert cipher != text
    assert keyed_transposition.columnar_decrypt(cipher, "SECURITY") == text


def test_double_transposition_roundtrip():
    text = "HN BLACKBOX SECURITY LAB"
    first = keyed_transposition.columnar_encrypt(text, "FIRST")
    cipher = keyed_transposition.columnar_encrypt(first, "SECOND")
    assert cipher != text
    assert keyed_transposition.columnar_decrypt(keyed_transposition.columnar_decrypt(cipher, "SECOND"), "FIRST") == text


def test_stego_png_roundtrip(tmp_path):
    src = tmp_path / "original.png"
    out = tmp_path / "hidden.png"
    Image.new("RGB", (80, 80), (80, 120, 160)).save(src)
    message = "HN BlackBox Secret — LSB test"
    result = stego.encode(str(src), str(out), message)
    assert result["message_bytes"] == len(message.encode("utf-8"))
    assert stego.decode(str(out)) == message
    report = stego.inspect_lsb(str(out), 128)
    assert report["payload"]["detected"] is True


def test_stego_capacity_guard(tmp_path):
    src = tmp_path / "tiny.png"
    Image.new("RGB", (4, 4), (1, 2, 3)).save(src)
    cap = stego.capacity_bytes(str(src))
    assert cap >= 0
    try:
        stego.encode(str(src), str(tmp_path / "out.png"), "x" * (cap + 1))
    except ValueError as exc:
        assert "too large" in str(exc).lower()
    else:
        raise AssertionError("capacity guard did not reject an oversized payload")
