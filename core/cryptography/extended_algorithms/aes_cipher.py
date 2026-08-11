# -*- coding: utf-8 -*-
"""AES-256 educational wrapper. Requires cryptography."""
from __future__ import annotations
import base64, hashlib
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
except ImportError:
    Cipher = algorithms = modes = padding = None

def _require():
    if Cipher is None: raise RuntimeError("AES requires the 'cryptography' package. Install requirements.txt.")

def _key(key):
    return hashlib.sha256(key.encode()).digest()

def encrypt(text,key):
    _require()
    k=_key(key); iv=__import__('secrets').token_bytes(16)
    pad=padding.PKCS7(128).padder(); data=pad.update(text.encode())+pad.finalize()
    enc=Cipher(algorithms.AES(k),modes.CBC(iv)).encryptor()
    return base64.b64encode(iv+enc.update(data)+enc.finalize()).decode()
def decrypt(text,key):
    _require()
    try: raw=base64.b64decode(text.encode(),validate=True)
    except Exception as e: raise ValueError("Invalid AES ciphertext.") from e
    if len(raw)<32: raise ValueError("Invalid AES ciphertext.")
    iv,ct=raw[:16],raw[16:]
    dec=Cipher(algorithms.AES(_key(key)),modes.CBC(iv)).decryptor()
    padded=dec.update(ct)+dec.finalize()
    try:
        un=padding.PKCS7(128).unpadder(); return (un.update(padded)+un.finalize()).decode()
    except Exception as e: raise ValueError("Wrong AES key or corrupted ciphertext.") from e
