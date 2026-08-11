# -*- coding: utf-8 -*-
"""
rail_fence.py

تشفير السياج/الزقزاق (Rail Fence Cipher) — نكتب النص بشكل متعرّج (زقزاق)
على عدد "قضبان" (rails) يحدده المفتاح، وبعدين نقرأ الناتج صف صف.
"""


def encrypt(text: str, rails: int) -> str:
    rails = int(rails)
    if rails < 2:
        raise ValueError("عدد القضبان (rails) لازم يكون 2 على الأقل.")
    if rails >= len(text):
        return text

    fence = [[] for _ in range(rails)]
    row, direction = 0, 1
    for ch in text:
        fence[row].append(ch)
        if row == 0:
            direction = 1
        elif row == rails - 1:
            direction = -1
        row += direction

    return "".join("".join(r) for r in fence)


def decrypt(cipher: str, rails: int) -> str:
    rails = int(rails)
    if rails < 2:
        raise ValueError("عدد القضبان (rails) لازم يكون 2 على الأقل.")
    if rails >= len(cipher):
        return cipher

    pattern = []
    row, direction = 0, 1
    for _ in cipher:
        pattern.append(row)
        if row == 0:
            direction = 1
        elif row == rails - 1:
            direction = -1
        row += direction

    counts = [pattern.count(r) for r in range(rails)]
    pos = 0
    rail_contents = []
    for count in counts:
        rail_contents.append(list(cipher[pos:pos + count]))
        pos += count

    rail_pointers = [0] * rails
    result = []
    for r in pattern:
        result.append(rail_contents[r][rail_pointers[r]])
        rail_pointers[r] += 1

    return "".join(result)
