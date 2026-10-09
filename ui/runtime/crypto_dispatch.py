"""Adapter boundary for HN BlackBox cryptography.

IMPORTANT: no cipher implementation lives here. Calls are delegated to the
existing modules without changing their algorithms or source files.
"""
from __future__ import annotations
import re
from core.cryptography.classical import additional
from core.cryptography.classical.additional import hill_cipher
from core.cryptography.classical.required import keyed_transposition, double_transposition
from core.cryptography.modern import aes_cipher, rsa as educational_rsa, hashing
from core.cryptography.classical.required import (
    caesar as required_caesar,
    vigenere as required_vigenere,
    affine as required_affine,
    autokey as required_autokey,
    rail_fence as required_rail_fence,
    additive as required_additive,
    multiplicative as required_multiplicative,
)
from core.cryptography.modern import des as des_cipher


def reparse_rsa(value: str):
    pairs = dict(re.findall(r"([edn])\s*=\s*([0-9]+)", value))
    if not all(x in pairs for x in ("e", "d", "n")):
        raise ValueError("RSA key must contain e, d and n")
    return {k: int(v) for k, v in pairs.items()}


def execute_crypto(algorithm: str, values: dict[str, str], operation: str, text: str) -> str:
    """Execute one existing algorithm; intentionally mirrors the old dispatch."""
    k, vals, op = algorithm, values, operation
    if k == "caesar": return required_caesar.encrypt(text, int(vals["shift"])) if op == "encrypt" else required_caesar.decrypt(text, int(vals["shift"]))
    if k == "additive": return required_additive.encrypt(text, int(vals["shift"])) if op == "encrypt" else required_additive.decrypt(text, int(vals["shift"]))
    if k == "multiplicative": return required_multiplicative.encrypt(text, int(vals["key"])) if op == "encrypt" else required_multiplicative.decrypt(text, int(vals["key"]))
    if k == "vigenere": return required_vigenere.encrypt(text, vals["word"]) if op == "encrypt" else required_vigenere.decrypt(text, vals["word"])
    if k == "playfair": return additional.playfair.encrypt(text, vals["word"]) if op == "encrypt" else additional.playfair.decrypt(text, vals["word"])
    if k == "railfence": return required_rail_fence.encrypt(text, int(vals["rails"])) if op == "encrypt" else required_rail_fence.decrypt(text, int(vals["rails"]))
    if k == "columnar": return keyed_transposition.columnar_encrypt(text, vals["word"]) if op == "encrypt" else keyed_transposition.columnar_decrypt(text, vals["word"])
    if k == "atbash": return additional.atbash.atbash(text)
    if k == "rot13": return additional.rot13.rot13(text)
    if k == "affine": return required_affine.encrypt(text, int(vals["a"]), int(vals["b"])) if op == "encrypt" else required_affine.decrypt(text, int(vals["a"]), int(vals["b"]))
    if k == "hill":
        key = tuple(int(vals[x]) for x in ("a", "b", "c", "d"))
        return hill_cipher.encrypt(text, key) if op == "encrypt" else hill_cipher.decrypt(text, key)
    if k == "beaufort": return additional.beaufort.beaufort(text, vals["word"])
    if k == "polybius": return additional.polybius.polybius_encrypt(text) if op == "encrypt" else additional.polybius.polybius_decrypt(text)
    if k == "adfgvx": return additional.adfgvx.adfgvx_encrypt(text, vals["word"]) if op == "encrypt" else additional.adfgvx.adfgvx_decrypt(text, vals["word"])
    if k == "bacon": return additional.bacon.bacon_encrypt(text) if op == "encrypt" else additional.bacon.bacon_decrypt(text)
    if k == "morse": return additional.morse.morse_encrypt(text) if op == "encrypt" else additional.morse.morse_decrypt(text)
    if k == "autokey": return required_autokey.encrypt(text, vals["word"]) if op == "encrypt" else required_autokey.decrypt(text, vals["word"])
    if k == "otp": return additional.otp.otp_encrypt(text, vals["word"]) if op == "encrypt" else additional.otp.otp_decrypt(text, vals["word"])
    if k == "aes": return aes_cipher.encrypt(text, vals["word"]) if op == "encrypt" else aes_cipher.decrypt(text, vals["word"])
    if k == "des": return des_cipher.encrypt(text, vals["key"]) if op == "encrypt" else des_cipher.decrypt(text, vals["key"])
    if k == "keyed_transposition": return keyed_transposition.columnar_encrypt(text, vals["word"]) if op == "encrypt" else keyed_transposition.columnar_decrypt(text, vals["word"])
    if k == "double_transposition": return double_transposition.encrypt(text, vals["word1"], vals["word2"]) if op == "encrypt" else double_transposition.decrypt(text, vals["word1"], vals["word2"])
    if k == "rsa":
        m = reparse_rsa(vals["key"])
        return educational_rsa.rsa_encrypt(text, m["e"], m["n"]) if op == "encrypt" else educational_rsa.rsa_decrypt(text, m["d"], m["n"])
    if k == "hash": return hashing.hash_text(text, (vals["word"] or "SHA-256").lower().replace("-", ""))
    raise ValueError("Unknown algorithm")
