# -*- coding: utf-8 -*-
"""
hill_cipher.py

إضافة إضافية (مو من ضمن الخوارزميات المطلوبة بالتكليف الأصلي، أضفتها
كدرجة تحدّي إضافي). تشفير هيل يستخدم الجبر الخطي فعليًا — النص يتحول
لمتجهات أرقام، ثم يُضرب بمصفوفة 2×2 (المفتاح) modulo 26. لفك التشفير
نحتاج معكوس المصفوفة modulo 26، وهذا يشتغل بس لو محدد المصفوفة (determinant)
عنده معكوس ضربي مع 26 (يعني gcd(det, 26) = 1).

نفس اتفاقية Playfair: يشتغل على أحرف فقط، الناتج بأحرف كبيرة، ولو طول
النص فردي نضيف X بالنهاية.
"""

import math

ALPHABET_SIZE = 26


def _mod_inverse(a: int, m: int) -> int:
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"العدد {a} ماله معكوس ضربي بالمقياس {m}.")


def _validate_key(key):
    if len(key) != 4:
        raise ValueError("مفتاح Hill Cipher لازم يكون 4 أرقام (مصفوفة 2×2): a b c d.")
    a, b, c, d = key
    det = (a * d - b * c) % ALPHABET_SIZE
    if math.gcd(det, ALPHABET_SIZE) != 1:
        raise ValueError(
            f"هذي المصفوفة غير صالحة للتشفير (determinant={det} ما إله معكوس مع 26). "
            "جرّب أرقام ثانية."
        )
    return det


def _prepare_letters(text: str):
    letters = [c.upper() for c in text if c.isalpha()]
    if len(letters) % 2 != 0:
        letters.append("X")
    return letters


def encrypt(text: str, key) -> str:
    a, b, c, d = key
    _validate_key(key)
    letters = _prepare_letters(text)

    result = []
    for i in range(0, len(letters), 2):
        x1 = ord(letters[i]) - ord("A")
        x2 = ord(letters[i + 1]) - ord("A")
        y1 = (a * x1 + b * x2) % ALPHABET_SIZE
        y2 = (c * x1 + d * x2) % ALPHABET_SIZE
        result.append(chr(y1 + ord("A")))
        result.append(chr(y2 + ord("A")))

    return "".join(result)


def decrypt(cipher: str, key) -> str:
    a, b, c, d = key
    det = _validate_key(key)
    det_inv = _mod_inverse(det, ALPHABET_SIZE)

    # معكوس المصفوفة [[a,b],[c,d]] هو det_inv * [[d,-b],[-c,a]] mod 26
    ia = (det_inv * d) % ALPHABET_SIZE
    ib = (det_inv * -b) % ALPHABET_SIZE
    ic = (det_inv * -c) % ALPHABET_SIZE
    id_ = (det_inv * a) % ALPHABET_SIZE

    letters = [c.upper() for c in cipher if c.isalpha()]
    if len(letters) % 2 != 0:
        raise ValueError("نص Hill Cipher المشفّر لازم يكون طوله زوجي.")

    result = []
    for i in range(0, len(letters), 2):
        y1 = ord(letters[i]) - ord("A")
        y2 = ord(letters[i + 1]) - ord("A")
        x1 = (ia * y1 + ib * y2) % ALPHABET_SIZE
        x2 = (ic * y1 + id_ * y2) % ALPHABET_SIZE
        result.append(chr(x1 + ord("A")))
        result.append(chr(x2 + ord("A")))

    return "".join(result)
