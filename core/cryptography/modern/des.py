# -*- coding: utf-8 -*-
"""Educational single-DES implementation with key-schedule tracing.

DES is obsolete for real-world security. This module exists for coursework,
visualization, and interoperability/testing only.
"""
from __future__ import annotations
import base64

# FIPS 46-3 tables
IP = [
58,50,42,34,26,18,10,2,60,52,44,36,28,20,12,4,62,54,46,38,30,22,14,6,
64,56,48,40,32,24,16,8,57,49,41,33,25,17,9,1,59,51,43,35,27,19,11,3,
61,53,45,37,29,21,13,5,63,55,47,39,31,23,15,7]
FP = [
40,8,48,16,56,24,64,32,39,7,47,15,55,23,63,31,38,6,46,14,54,22,62,30,
37,5,45,13,53,21,61,29,36,4,44,12,52,20,60,28,35,3,43,11,51,19,59,27,
34,2,42,10,50,18,58,26,33,1,41,9,49,17,57,25]
E = [32,1,2,3,4,5,4,5,6,7,8,9,8,9,10,11,12,13,12,13,14,15,16,17,
16,17,18,19,20,21,20,21,22,23,24,25,24,25,26,27,28,29,28,29,30,31,32,1]
PBOX = [16,7,20,21,29,12,28,17,1,15,23,26,5,18,31,10,2,8,24,14,32,27,3,9,19,13,30,6,22,11,4,25]
PC1 = [57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,59,51,43,35,27,19,11,3,
       60,52,44,36,63,55,47,39,31,23,15,7,62,54,46,38,30,22,14,6,
       61,53,45,37,29,21,13,5,28,20,12,4]
PC2 = [14,17,11,24,1,5,3,28,15,6,21,10,23,19,12,4,26,8,16,7,27,20,13,2,
       41,52,31,37,47,55,30,40,51,45,33,48,44,49,39,56,34,53,46,42,50,36,29,32]
SHIFTS = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]

SBOXES = [
[[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],[0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],[4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],[15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]],
[[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],[3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],[0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],[13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]],
[[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],[13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],[13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],[1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]],
[[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],[13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],[10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],[3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],
[[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],[14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],[4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],[11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]],
[[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],[10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],[9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],[4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]],
[[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],[13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],[1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],[6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]],
[[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],[1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],[7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],[2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]]
]

def _permute(block: int, table: list[int], in_bits: int) -> int:
    out = 0
    for pos in table:
        out = (out << 1) | ((block >> (in_bits - pos)) & 1)
    return out

def _rot28(x: int, n: int) -> int:
    return ((x << n) | (x >> (28-n))) & 0x0FFFFFFF

def subkeys(key8: bytes) -> list[int]:
    if len(key8) != 8:
        raise ValueError("DES key must be exactly 8 bytes.")
    k56 = _permute(int.from_bytes(key8, "big"), PC1, 64)
    c, d = k56 >> 28, k56 & 0x0FFFFFFF
    keys = []
    for shift in SHIFTS:
        c, d = _rot28(c, shift), _rot28(d, shift)
        keys.append(_permute((c << 28) | d, PC2, 56))
    return keys

def _sbox(x: int) -> int:
    out = 0
    for i in range(8):
        six = (x >> (42 - i*6)) & 0x3F
        row = ((six >> 5) & 1) * 2 + (six & 1)
        col = (six >> 1) & 0xF
        out = (out << 4) | SBOXES[i][row][col]
    return out

def _f(r: int, k: int) -> int:
    e = _permute(r, E, 32)
    x = e ^ k
    return _permute(_sbox(x), PBOX, 32)

def _f_trace(r: int, k: int) -> dict:
    e = _permute(r, E, 32)
    x = e ^ k
    s = _sbox(x)
    p = _permute(s, PBOX, 32)
    return {"expanded": f"{e:012X}", "xor": f"{x:012X}", "sbox": f"{s:08X}", "pbox": f"{p:08X}", "f": f"{p:08X}"}

def trace_block(block8: bytes, keys: list[int], decrypt_mode: bool = False) -> dict:
    if len(block8) != 8:
        raise ValueError("DES block must be 8 bytes.")
    x = _permute(int.from_bytes(block8, "big"), IP, 64)
    l, r = x >> 32, x & 0xFFFFFFFF
    rows = []
    use_keys = list(reversed(keys)) if decrypt_mode else keys
    for i, k in enumerate(use_keys, 1):
        f = _f_trace(r, k)
        nl, nr = r, l ^ int(f["f"], 16)
        rows.append({"round": i, "key_hex": f"{k:012X}", "l_in": f"{l:08X}", "r_in": f"{r:08X}", "expanded": f["expanded"], "xor": f["xor"], "sbox": f["sbox"], "pbox": f["pbox"], "l_out": f"{nl:08X}", "r_out": f"{nr:08X}"})
        l, r = nl, nr
    final = _permute((r << 32) | l, FP, 64)
    return {"ip": f"{x:016X}", "rounds": rows, "final": f"{final:016X}"}

def encrypt_block(block8: bytes, keys: list[int]) -> bytes:
    if len(block8) != 8: raise ValueError("DES block must be 8 bytes.")
    x = _permute(int.from_bytes(block8, "big"), IP, 64)
    l, r = x >> 32, x & 0xFFFFFFFF
    for k in keys:
        l, r = r, l ^ _f(r, k)
    return _permute((r << 32) | l, FP, 64).to_bytes(8, "big")

def decrypt_block(block8: bytes, keys: list[int]) -> bytes:
    return encrypt_block(block8, list(reversed(keys)))

def _pad(data: bytes) -> bytes:
    n = 8 - (len(data) % 8)
    return data + bytes([n])*n

def _unpad(data: bytes) -> bytes:
    if not data or data[-1] < 1 or data[-1] > 8 or data[-data[-1]:] != bytes([data[-1]])*data[-1]:
        raise ValueError("Invalid DES padding: wrong key or corrupted ciphertext.")
    return data[:-data[-1]]

def encrypt(text: str, key: str) -> str:
    raw_key = key.encode("utf-8")
    if len(raw_key) != 8:
        raise ValueError("DES key must be exactly 8 UTF-8 bytes (for example: HNKEY123).")
    # Fixed zero IV keeps the educational output deterministic for classroom tracing.
    iv = b"\x00"*8
    keys = subkeys(raw_key)
    data = _pad(text.encode("utf-8"))
    prev = iv
    out = bytearray(iv)
    for i in range(0, len(data), 8):
        block = bytes(a ^ b for a,b in zip(data[i:i+8], prev))
        enc = encrypt_block(block, keys); out.extend(enc); prev=enc
    return base64.b64encode(bytes(out)).decode("ascii")

def decrypt(ciphertext: str, key: str) -> str:
    raw_key = key.encode("utf-8")
    if len(raw_key) != 8:
        raise ValueError("DES key must be exactly 8 UTF-8 bytes.")
    try: raw = base64.b64decode(ciphertext, validate=True)
    except Exception as e: raise ValueError("DES ciphertext must be valid Base64.") from e
    if len(raw) < 16 or (len(raw)-8) % 8:
        raise ValueError("Invalid DES ciphertext length.")
    keys = subkeys(raw_key)
    iv, ct = raw[:8], raw[8:]
    prev, plain = iv, bytearray()
    for i in range(0, len(ct), 8):
        enc=ct[i:i+8]; dec=decrypt_block(enc, keys)
        plain.extend(a ^ b for a,b in zip(dec, prev)); prev=enc
    try: return _unpad(bytes(plain)).decode("utf-8")
    except UnicodeDecodeError as e: raise ValueError("Wrong DES key or invalid UTF-8 plaintext.") from e

def trace(key: str) -> dict:
    raw_key=key.encode("utf-8")
    if len(raw_key)!=8: raise ValueError("DES key must be exactly 8 UTF-8 bytes.")
    ks=subkeys(raw_key)
    return {
        "key_hex": raw_key.hex().upper(),
        "rounds": [{"round":i+1,"subkey_hex":f"{k:012X}","shift":SHIFTS[i]} for i,k in enumerate(ks)],
    }

def trace_execution(text: str, key: str, decrypt_mode: bool = False) -> dict:
    raw = text.encode("utf-8")
    if decrypt_mode:
        raise ValueError("trace_execution expects plaintext text; use trace_block for ciphertext blocks.")
    keys = subkeys(key.encode("utf-8"))
    data = _pad(raw)
    first = data[:8]
    return trace_block(first, keys, False)
