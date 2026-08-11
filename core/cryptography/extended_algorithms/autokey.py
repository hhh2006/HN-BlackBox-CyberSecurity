# -*- coding: utf-8 -*-
"""
autokey.py

تشفير الأوتوكي (Autokey Cipher) — تحسين على Vigenère. المشكلة بـ Vigenère
إن المفتاح يتكرر، وهذا يخلي تحليل التكرار (Kasiski) ممكن يكسره. بالأوتوكي
بدل ما نكرر كلمة المفتاح، نمدّها بالنص الصريح نفسه بعد أول استخدام:

    مفتاح التيار الفعلي = كلمة_المفتاح + النص_الصريح (بالحروف فقط)

يعني كل حرف تشفير يعتمد على حرف سابق من الرسالة نفسها، مو نمط متكرر
يسهل اكتشافه. فك التشفير يصير تدريجي: نفك أول حرف بالمفتاح المعطى،
والحرف اللي طلع نضيفه لمفتاح التيار عشان نفك اللي بعده، وهكذا.
"""

ALPHABET_SIZE = 26


def _clean_key(key: str):
    letters = [c.upper() for c in key if c.isalpha()]
    if not letters:
        raise ValueError("مفتاح Autokey لازم يحتوي على حرف واحد أبجدي على الأقل.")
    return letters


def encrypt(text: str, key: str) -> str:
    key_letters = _clean_key(key)
    plain_letters = [c.upper() for c in text if c.isalpha()]
    keystream = (key_letters + plain_letters)[: len(plain_letters)]

    result = []
    ks_pos = 0
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            shift = ord(keystream[ks_pos]) - ord("A")
            x = ord(ch.upper()) - ord("A")
            y = (x + shift) % ALPHABET_SIZE
            new_ch = chr(y + ord("A"))
            result.append(new_ch if ch.isupper() else new_ch.lower())
            ks_pos += 1
        else:
            result.append(ch)
    return "".join(result)


def decrypt(cipher: str, key: str) -> str:
    keystream = _clean_key(key)  # يكبر تدريجيًا كل ما فكينا حرف جديد

    result = []
    ks_pos = 0
    for ch in cipher:
        if ch.isalpha():
            base_upper = ch.isupper()
            shift = ord(keystream[ks_pos]) - ord("A")
            y = ord(ch.upper()) - ord("A")
            x = (y - shift) % ALPHABET_SIZE
            plain_letter = chr(x + ord("A"))
            result.append(plain_letter if base_upper else plain_letter.lower())
            keystream.append(plain_letter)  # نوسّع مفتاح التيار بالحرف اللي فككناه للتو
            ks_pos += 1
        else:
            result.append(ch)
    return "".join(result)
