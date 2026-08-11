# -*- coding: utf-8 -*-
"""Additive (shift) cipher kept separate from Caesar for the requested core rack."""
import string

ALPHABET = string.ascii_uppercase

def _shift_char(ch: str, k: int) -> str:
    if ch.isalpha() and ch.upper() in ALPHABET:
        base = ord('A') if ch.isupper() else ord('a')
        return chr((ord(ch) - base + k) % 26 + base)
    return ch

def encrypt(text: str, key: int) -> str:
    return ''.join(_shift_char(ch, int(key)) for ch in text)

def decrypt(text: str, key: int) -> str:
    return ''.join(_shift_char(ch, -int(key)) for ch in text)
