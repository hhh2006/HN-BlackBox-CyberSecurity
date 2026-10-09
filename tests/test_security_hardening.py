from core.cryptography.modern import aes_cipher
from core.cryptography.modern import secure_rsa


def test_aes_new_format_is_authenticated_and_randomized():
    a = aes_cipher.encrypt("HN BlackBox — secure", "secret")
    b = aes_cipher.encrypt("HN BlackBox — secure", "secret")
    assert a != b
    assert a != ""
    assert aes_cipher.decrypt(a, "secret") == "HN BlackBox — secure"
    bad = a[:-2] + ("AA" if a[-2:] != "AA" else "BB")
    try:
        aes_cipher.decrypt(bad, "secret")
    except ValueError:
        pass
    else:
        raise AssertionError("AES-GCM tampering must be rejected")


def test_aes_legacy_cbc_compatibility():
    import base64, hashlib, secrets
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    key = hashlib.sha256(b"legacy").digest(); iv = secrets.token_bytes(16)
    pad = padding.PKCS7(128).padder(); data = pad.update(b"legacy text") + pad.finalize()
    enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    legacy = base64.b64encode(iv + enc.update(data) + enc.finalize()).decode()
    assert aes_cipher.decrypt(legacy, "legacy") == "legacy text"


def test_secure_rsa_oaep_roundtrip():
    private, public = secure_rsa.generate_keypair(2048)
    msg = b"HN BlackBox secure RSA"
    ct = secure_rsa.encrypt(msg, public)
    assert secure_rsa.decrypt(ct, private) == msg
