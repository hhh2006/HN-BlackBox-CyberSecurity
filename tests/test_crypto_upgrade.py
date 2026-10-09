import tempfile
from pathlib import Path
from core.cryptography.modern import des
from core.cryptography.steganography import steganography as stego
from PIL import Image

def test_des_known_vector():
    key=bytes.fromhex("133457799BBCDFF1")
    plain=bytes.fromhex("0123456789ABCDEF")
    expected=bytes.fromhex("85E813540F0AB405")
    assert des.encrypt_block(plain, des.subkeys(key)) == expected
    assert des.decrypt_block(expected, des.subkeys(key)) == plain

def test_des_roundtrip_and_trace():
    c=des.encrypt("Hello HN BlackBox","HNKEY123")
    assert des.decrypt(c,"HNKEY123")=="Hello HN BlackBox"
    assert len(des.trace("HNKEY123")["rounds"])==16

def test_des_wrong_key():
    c=des.encrypt("secret","HNKEY123")
    try:
        des.decrypt(c,"WRONG123")
    except ValueError:
        pass
    else:
        assert False, "wrong DES key must fail"

def test_lsb_roundtrip(tmp_path):
    src=tmp_path/"source.png"; out=tmp_path/"embedded.png"
    Image.new("RGB",(64,64),(20,40,60)).save(src)
    stego.encode(str(src),str(out),"HN BLACKBOX SECRET")
    assert stego.decode(str(out))=="HN BLACKBOX SECRET"

def test_lsb_rejects_non_image(tmp_path):
    p=tmp_path/"bad.txt"; p.write_text("not image",encoding="utf-8")
    try: stego.capacity_bytes(str(p))
    except ValueError: pass
    else: assert False

def test_lsb_inspector(tmp_path):
    src=tmp_path/"inspect.png"
    Image.new("RGB",(32,32),(17,34,51)).save(src)
    report=stego.inspect_lsb(str(src), 32)
    assert report["width"] == 32 and report["height"] == 32
    assert set(report["plane_density_percent"]) == {"R","G","B"}
    assert len(report["lsb_stream"]) == 32*3
    assert report["payload"]["detected"] is False
