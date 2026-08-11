# -*- coding: utf-8 -*-
"""Local cryptography intelligence helpers for HN BlackBox.
Educational analysis only; no external scanning or network operations.
"""
from __future__ import annotations
import base64, binascii, hashlib, math, string
from collections import Counter

ALGO_META={
 'caesar':('Classical','Substitution','26 shifts','LOW','educational'),
 'vigenere':('Classical','Polyalphabetic','26^key_length','LOW','educational'),
 'playfair':('Classical','Digraph substitution','5x5 square','LOW','educational'),
 'railfence':('Classical','Transposition','rail count','LOW','educational'),
 'affine':('Classical','Substitution','312 valid pairs','LOW','educational'),
 'autokey':('Classical','Polyalphabetic','keyword dependent','LOW','educational'),
 'aes':('Modern','Symmetric block cipher','256-bit key demo','HIGH','educational'),
 'rsa':('Modern','Asymmetric','key-pair dependent','HIGH','educational'),
 'hash':('Integrity','Digest','fixed output','N/A','one-way'),
}

def shannon_entropy(text:str)->float:
    if not text:return 0.0
    n=len(text); c=Counter(text)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def _looks_base64(s):
    t=''.join(s.split())
    if len(t)<8 or len(t)%4:return False
    try: base64.b64decode(t,validate=True); return True
    except Exception:return False

def analyze_payload(text:str):
    stripped=text.strip(); ent=shannon_entropy(text)
    printable=sum(ch in string.printable for ch in text)/max(1,len(text))
    counts=Counter(ch.upper() for ch in text if ch.isalpha())
    common=', '.join(f'{k}:{v}' for k,v in counts.most_common(8)) or '—'
    signals=[]
    if _looks_base64(stripped): signals.append('BASE64-LIKE')
    if all(c in '01 \n\t' for c in stripped) and stripped.replace(' ','').replace('\n',''):
        signals.append('BINARY-LIKE')
    if all(c in '0123456789abcdefABCDEF' for c in stripped) and len(stripped.replace(' ',''))%2==0 and len(stripped)>8: signals.append('HEX-LIKE')
    if ent>4.5: signals.append('HIGHER ENTROPY')
    if printable<0.75: signals.append('NON-PRINTABLE / ENCODED')
    report=(
      'HN BLACKBOX // PAYLOAD ANALYZER\n'
      '══════════════════════════════════════════════════════\n'
      f'LENGTH             : {len(text):,} chars\n'
      f'SHANNON ENTROPY    : {ent:.3f} bits/char\n'
      f'PRINTABLE RATIO    : {printable*100:.1f}%\n'
      f'SIGNALS             : {", ".join(signals) if signals else "NONE / PLAIN-TEXT-LIKE"}\n'
      f'TOP LETTERS         : {common}\n'
      'NOTE                : Heuristics are indicators, not proof of an algorithm.\n'
    )
    return {'entropy':ent,'signals':signals,'report':report}

def compare_algorithms(keys):
    lines=['HN BLACKBOX // ALGORITHM MATRIX','════════════════════════════════════════════════════════════════','ALGORITHM        FAMILY       TRANSFORM             KEY / STATE        PROFILE']
    for k in keys:
        m=ALGO_META.get(k)
        if not m: continue
        lines.append(f'{k.upper():<16} {m[0]:<11} {m[1]:<21} {m[2]:<18} {m[3]}')
    lines += ['', 'DESIGN NOTE: classical ciphers are for learning/history; modern primitives need vetted libraries and safe modes for production.']
    return '\n'.join(lines)

def key_profile(algo,key):
    key=str(key or '')
    bits=len(key.encode())*8
    entropy=shannon_entropy(key)
    if algo=='caesar': space=26
    elif algo in ('aes',): space=2**256
    elif algo=='rsa': space='key-pair / modulus dependent'
    elif algo=='hash': space='not a key; digest function'
    else: space=f'~2^{min(256,max(1,bits))} upper bound from raw bytes'
    return (f'HN BLACKBOX // KEY PROFILE\n\nALGORITHM : {algo.upper()}\nKEY BYTES : {len(key.encode())}\nRAW BITS  : {bits}\nKEY ENTROPY: {entropy:.3f} bits/char\nKEY SPACE : {space}\n\nReminder: length is not the same as unpredictability. Never treat this estimate as a production security audit.')
