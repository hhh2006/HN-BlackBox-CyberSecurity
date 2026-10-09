
from core.cryptography.classical import additional as classical
from core.cryptography.modern import aes_cipher, rsa as educational_rsa, hashing

def test_atbash(): assert classical.atbash.atbash("HELLO") == "SVOOL"
def test_rot13(): assert classical.rot13.rot13("HELLO") == "URYYB"
def test_columnar_roundtrip():
    c=__import__("core.cryptography.classical.required", fromlist=["keyed_transposition"]).keyed_transposition.columnar_encrypt("WEAREDISCOVERED","ZEBRAS")
    assert __import__("core.cryptography.classical.required", fromlist=["keyed_transposition"]).keyed_transposition.columnar_decrypt(c,"ZEBRAS")=="WEAREDISCOVERED"
def test_beaufort_roundtrip():
    c=classical.beaufort.beaufort("HELLO","KEY")
    assert classical.beaufort.beaufort(c,"KEY")=="HELLO"
def test_polybius_roundtrip(): assert classical.polybius.polybius_decrypt(classical.polybius.polybius_encrypt("HELLO"))=="HELLO"
def test_bacon_roundtrip(): assert classical.bacon.bacon_decrypt(classical.bacon.bacon_encrypt("HELLO"))=="HELLO"
def test_morse_roundtrip(): assert classical.morse.morse_decrypt(classical.morse.morse_encrypt("SOS"))=="SOS"
def test_adfgvx_roundtrip():
    c=classical.adfgvx.adfgvx_encrypt("HELLO123","KEY")
    assert classical.adfgvx.adfgvx_decrypt(c,"KEY")=="HELLO123"
def test_otp_roundtrip():
    k=classical.otp.otp_key(32); c=classical.otp.otp_encrypt("Hello",k); assert classical.otp.otp_decrypt(c,k)=="Hello"
def test_rsa_roundtrip():
    e,d,n=educational_rsa.rsa_generate(256); c=educational_rsa.rsa_encrypt("Hi",e,n); assert educational_rsa.rsa_decrypt(c,d,n)=="Hi"
def test_hash(): assert len(hashing.hash_text("x","sha256"))==64
def test_aes_roundtrip():
    c=aes_cipher.encrypt("Hello","key"); assert aes_cipher.decrypt(c,"key")=="Hello"
