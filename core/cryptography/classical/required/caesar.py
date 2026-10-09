# -*- coding: utf-8 -*-
"""
caesar.py

أبسط خوارزمية تشفير كلاسيكية — كل حرف ينزاح بعدد ثابت (المفتاح) بالأبجدية.
مثال: A بمفتاح 3 تصير D. نحافظ على حالة الحرف (كبير/صغير) وما نلمس
أي رمز مو حرف إنجليزي (أرقام، مسافات، علامات ترقيم).
"""

ALPHABET_SIZE = 26


def _shift_char(ch: str, key: int) -> str:
    if ch.isupper():
        base = ord("A")
    elif ch.islower():
        base = ord("a")
    else:
        return ch
    return chr((ord(ch) - base + key) % ALPHABET_SIZE + base)


def encrypt(text: str, key: int) -> str:
    key = int(key) % ALPHABET_SIZE
    return "".join(_shift_char(ch, key) for ch in text)


def decrypt(text: str, key: int) -> str:
    key = int(key) % ALPHABET_SIZE
    return "".join(_shift_char(ch, -key) for ch in text)


def brute_force(ciphertext: str):
    """يرجّع كل الاحتمالات الـ 26 لفك التشفير بدون معرفة المفتاح — يفيد بهجمات القوة الغاشمة."""
    return [(key, decrypt(ciphertext, key)) for key in range(ALPHABET_SIZE)]
