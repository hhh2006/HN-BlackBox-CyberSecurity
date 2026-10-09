"""Production-oriented RSA helpers kept separate from the educational RSA demo."""
from __future__ import annotations
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def generate_keypair(bits: int = 3072) -> tuple[bytes, bytes]:
    if bits < 2048:
        raise ValueError("RSA security keys must be at least 2048 bits.")
    private = rsa.generate_private_key(public_exponent=65537, key_size=bits)
    private_pem = private.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def encrypt(message: bytes, public_pem: bytes) -> bytes:
    public = serialization.load_pem_public_key(public_pem)
    return public.encrypt(
        message,
        padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )


def decrypt(ciphertext: bytes, private_pem: bytes) -> bytes:
    private = serialization.load_pem_private_key(private_pem, password=None)
    return private.decrypt(
        ciphertext,
        padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )
