"""Truthful, algorithm-specific visual models for the classical-cipher lab.

This module contains presentation data only. It never performs encryption, so the
visual layer cannot silently diverge from the cryptographic engines.
"""
from __future__ import annotations

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def stream_rows(text: str, result: str, key: str = "", algo: str = "caesar", limit: int = 42):
    src = text or ""
    out = result or ""
    rows = []
    for i in range(min(max(len(src), len(out)), limit)):
        a = src[i] if i < len(src) else "·"
        b = out[i] if i < len(out) else "·"
        if algo == "caesar":
            op = f"SHIFT {key}"
        elif algo == "additive":
            op = f"ADD {key} MOD 26"
        elif algo == "multiplicative":
            op = f"MUL ×{key} MOD 26"
        elif algo == "affine":
            op = f"{key} MOD 26"
        elif algo in {"vigenere", "autokey", "beaufort"}:
            letter = key[i % len(key)] if key else "?"
            op = f"KEY[{letter}]"
        elif algo == "atbash":
            op = "A↔Z MAP"
        elif algo == "rot13":
            op = "ROT +13"
        else:
            op = "TRANSFORM"
        rows.append((i + 1, a, op, b))
    return rows


def transposition_grid(text: str, key: str, passes: int = 1):
    clean_key = "".join(ch for ch in (key or "").upper() if ch.isalpha()) or "KEY"
    cols = len(clean_key)
    rows = max(1, (len(text or "") + cols - 1) // cols)
    matrix = []
    source = text or ""
    for r in range(rows):
        matrix.append([source[r * cols + c] if r * cols + c < len(source) else "·" for c in range(cols)])
    order = sorted(range(cols), key=lambda i: (clean_key[i], i))
    return matrix, clean_key, order, passes
