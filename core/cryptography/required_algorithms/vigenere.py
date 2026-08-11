# -*- coding: utf-8 -*-
"""
vigenere.py

تشفير فيجينير — نفس فكرة القيصرية بس كل حرف بالنص ينزاح بمقدار مختلف
حسب الحرف المقابل له بكلمة المفتاح (تتكرر الكلمة لين تغطي طول النص).
مثال: نص "HELLO" ومفتاح "KEY" -> المفتاح يتكرر "KEYKE".
نتجاهل الأحرف غير الأبجدية بالنص من حساب الإزاحة (بس نطبعها زي ما هي)،
ولا نحرّك مؤشر المفتاح إلا مع حرف أبجدي فعلي.
"""

ALPHABET_SIZE = 26
def _clean_key(key: str) -> str:
    letters = [c for c in key.upper() if c.isalpha()]
    if not letters:
        raise ValueError("مفتاح Vigenère لازم يحتوي على حرف واحد أبجدي على الأقل.")
    return "".join(letters)


def _process(text: str, key: str, sign: int) -> str:
    key = _clean_key(key)
    result = []
    key_index = 0
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            shift = ord(key[key_index % len(key)]) - ord("A") #تقنيه التدوير التلقائيه 
            
            new_ch = chr((ord(ch) - base + (sign * shift)) % ALPHABET_SIZE + base)
            result.append(new_ch)
            key_index += 1
        else:
            result.append(ch)
    return "".join(result)


def encrypt(text: str, key: str) -> str:
    return _process(text, key, sign=1)


def decrypt(text: str, key: str) -> str:
    return _process(text, key, sign=-1)
