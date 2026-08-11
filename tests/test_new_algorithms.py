
from core import classical, aes_cipher

def test_atbash(): assert classical.atbash("HELLO") == "SVOOL"
def test_rot13(): assert classical.rot13("HELLO") == "URYYB"
def test_columnar_roundtrip():
    c=classical.columnar_encrypt("WEAREDISCOVERED","ZEBRAS")
    assert classical.columnar_decrypt(c,"ZEBRAS")=="WEAREDISCOVERED"
def test_beaufort_roundtrip():
    c=classical.beaufort("HELLO","KEY")
    assert classical.beaufort(c,"KEY")=="HELLO"
def test_polybius_roundtrip(): assert classical.polybius_decrypt(classical.polybius_encrypt("HELLO"))=="HELLO"
def test_bacon_roundtrip(): assert classical.bacon_decrypt(classical.bacon_encrypt("HELLO"))=="HELLO"
def test_morse_roundtrip(): assert classical.morse_decrypt(classical.morse_encrypt("SOS"))=="SOS"
def test_adfgvx_roundtrip():
    c=classical.adfgvx_encrypt("HELLO123","KEY")
    assert classical.adfgvx_decrypt(c,"KEY")=="HELLO123"
def test_otp_roundtrip():
    k=classical.otp_key(32); c=classical.otp_encrypt("Hello",k); assert classical.otp_decrypt(c,k)=="Hello"
def test_rsa_roundtrip():
    e,d,n=classical.rsa_generate(256); c=classical.rsa_encrypt("Hi",e,n); assert classical.rsa_decrypt(c,d,n)=="Hi"
def test_hash(): assert len(classical.hash_text("x","sha256"))==64
def test_aes_roundtrip():
    c=aes_cipher.encrypt("Hello","key"); assert aes_cipher.decrypt(c,"key")=="Hello"
