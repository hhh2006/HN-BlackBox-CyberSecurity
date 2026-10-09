"""Double / combining transposition: two keyed columnar passes."""
from .keyed_transposition import columnar_encrypt, columnar_decrypt

def encrypt(text: str, key1: str, key2: str) -> str:
    return columnar_encrypt(columnar_encrypt(text, key1), key2)

def decrypt(text: str, key1: str, key2: str) -> str:
    return columnar_decrypt(columnar_decrypt(text, key2), key1)
