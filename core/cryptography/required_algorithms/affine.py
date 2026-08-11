# -*- coding: utf-8 -*-
"""
affine.py

تشفير الأفين (Affine Cipher) — كل حرف يتحول برقمه (A=0...Z=25) عبر
معادلة خطية: E(x) = (a*x + b) mod 26. المفتاح هنا رقمين (a, b) مو رقم
وحد. شرط أساسي: a لازم يكون أوّلي نسبيًا مع 26 (gcd(a,26)=1) وإلا
العملية ما ترجع قابلة للفك (مو bijective) — القيم الصالحة لـ a:
1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25.
"""

ALPHABET_SIZE = 26
VALID_A_VALUES = [a for a in range(1, ALPHABET_SIZE) if __import__("math").gcd(a, ALPHABET_SIZE) == 1]


def _mod_inverse(a: int, m: int) -> int:
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"القيمة {a} ما إلها معكوس ضربي (modular inverse) بالمقياس {m}.")


def _validate_a(a: int):
    if __import__("math").gcd(a, ALPHABET_SIZE) != 1: #القاسم المشترك
        raise ValueError(
            f"قيمة a={a} غير صالحة — لازم تكون أوّلية نسبيًا مع 26.\n"
            f"القيم المسموحة: {VALID_A_VALUES}"
        )


def encrypt(text: str, a: int, b: int) -> str:
    a, b = int(a), int(b)
    _validate_a(a)
    result = []
    for ch in text:
        if ch.isupper():
            base = ord("A")
        elif ch.islower():
            base = ord("a")
        else:
            result.append(ch)
            continue

        result.append(chr((((ord(ch) - base)*a+b)% ALPHABET_SIZE)+ base))
    return "".join(result)


def decrypt(text: str, a: int, b: int) -> str:
    a, b = int(a), int(b)
    _validate_a(a)
    a_inv = _mod_inverse(a, ALPHABET_SIZE)
    result = []
    for ch in text:
        if ch.isupper():
            base = ord("A")
        elif ch.islower():
            base = ord("a")
        else:
            result.append(ch)
            continue

        result.append(chr(((((ord(ch) - base)-b )* a_inv )% ALPHABET_SIZE)+ base))

    return "".join(result)
