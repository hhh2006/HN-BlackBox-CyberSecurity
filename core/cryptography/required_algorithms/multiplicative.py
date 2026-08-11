# -*- coding: utf-8 -*-
"""Multiplicative substitution cipher."""
import math

def _validate_key(key: int) -> int:
    key = int(key) % 26
    if math.gcd(key, 26) != 1:
        raise ValueError("Multiplicative key must be coprime with 26 (e.g. 1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25).")
    return key

def _inverse(key: int) -> int:
    key = _validate_key(key)
    return pow(key, -1, 26)

def _transform(text: str, key: int) -> str:
    out = []
    for ch in text:
        if ch.isalpha() and ch.upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            base = ord('A') if ch.isupper() else ord('a')
            x = ord(ch) - base
            out.append(chr((x * key) % 26 + base))
        else:
            out.append(ch)
    return ''.join(out)

def encrypt(text: str, key: int) -> str:
    return _transform(text, _validate_key(key))

def decrypt(text: str, key: int) -> str:
    return _transform(text, _inverse(key))
