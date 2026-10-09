# -*- coding: utf-8 -*-
"""AES encryption for HN BlackBox.

The default format is authenticated AES-256-GCM (HNA2).  The previous
AES-256-CBC format is retained as a read-only compatibility path so existing
saved ciphertexts remain decryptable.  New ciphertext must not use the legacy
unauthenticated CBC construction.
"""
from __future__ import annotations
import base64
import hashlib
import secrets

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import padding
except ImportError:
    Cipher = algorithms = modes = padding = AESGCM = None

PREFIX = b"HNA2:"
NONCE_SIZE = 12


def _require() -> None:
    if AESGCM is None:
        raise RuntimeError("AES requires the 'cryptography' package. Install requirements.txt.")


def _key(key: str) -> bytes:
    if not isinstance(key, str) or not key:
        raise ValueError("AES key is required.")
    return hashlib.sha256(key.encode("utf-8")).digest()


def encrypt(text: str, key: str) -> str:
    """Encrypt text with authenticated AES-256-GCM.

    Output is version-prefixed and Base64 encoded. A fresh random nonce is
    generated for every operation; authentication detects wrong keys and
    ciphertext modification.
    """
    _require()
    raw = text.encode("utf-8")
    nonce = secrets.token_bytes(NONCE_SIZE)
    ciphertext = AESGCM(_key(key)).encrypt(nonce, raw, None)
    return base64.b64encode(PREFIX + nonce + ciphertext).decode("ascii")


def _decrypt_legacy_cbc(raw: bytes, key: str) -> str:
    if Cipher is None or padding is None:
        _require()
    if len(raw) < 32 or (len(raw) - 16) % 16:
        raise ValueError("Invalid legacy AES ciphertext.")
    iv, ct = raw[:16], raw[16:]
    try:
        dec = Cipher(algorithms.AES(_key(key)), modes.CBC(iv)).decryptor()
        padded = dec.update(ct) + dec.finalize()
        un = padding.PKCS7(128).unpadder()
        return (un.update(padded) + un.finalize()).decode("utf-8")
    except Exception as exc:
        raise ValueError("Wrong AES key or corrupted ciphertext.") from exc


def decrypt(text: str, key: str) -> str:
    _require()
    try:
        raw = base64.b64decode(text.encode("ascii"), validate=True)
    except Exception as exc:
        raise ValueError("Invalid AES ciphertext.") from exc

    if raw.startswith(PREFIX):
        payload = raw[len(PREFIX):]
        if len(payload) < NONCE_SIZE + 16:
            raise ValueError("Invalid AES-GCM ciphertext.")
        nonce, ciphertext = payload[:NONCE_SIZE], payload[NONCE_SIZE:]
        try:
            plain = AESGCM(_key(key)).decrypt(nonce, ciphertext, None)
            return plain.decode("utf-8")
        except Exception as exc:
            raise ValueError("Wrong AES key or corrupted ciphertext.") from exc

    # Backward-compatible reader for the former AES-CBC format. It is never
    # emitted by encrypt().
    return _decrypt_legacy_cbc(raw, key)
