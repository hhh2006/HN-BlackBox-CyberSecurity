# -*- coding: utf-8 -*-
"""Additional educational cipher implementations used by HN BlackBox."""
from __future__ import annotations
import base64, hashlib, math, string
from typing import Iterable

ABC = string.ascii_uppercase

def _shift_char(ch, k):
    if ch.isalpha() and ch.upper() in ABC:
        alpha = ABC if ch.isupper() else ABC.lower()
        return alpha[(alpha.index(ch)+k)%26]
    return ch

def rot13(text): return ''.join(_shift_char(c, 13) for c in text)

def atbash(text):
    out=[]
    for c in text:
        if c.upper() in ABC:
            a=ABC if c.isupper() else ABC.lower()
            out.append(a[25-a.index(c)])
        else: out.append(c)
    return ''.join(out)

def beaufort(text, key):
    key=''.join(c for c in key.upper() if c in ABC)
    if not key: raise ValueError("Keyword is required.")
    out=[]; j=0
    for c in text:
        if c.upper() in ABC:
            x=ABC.index(c.upper()); k=ABC.index(key[j%len(key)])
            y=(k-x)%26
            out.append(ABC[y] if c.isupper() else ABC[y].lower()); j+=1
        else: out.append(c)
    return ''.join(out)

def _polybius_square():
    return "ABCDEFGHIKLMNOPQRSTUVWXYZ"

def polybius_encrypt(text):
    sq=_polybius_square(); out=[]
    for c in text.upper():
        if c=='J': c='I'
        if c in sq:
            i=sq.index(c); out.append(f"{i//5+1}{i%5+1}")
        elif c.isspace(): out.append(" ")
    return " ".join(out).replace("  "," ")

def polybius_decrypt(text):
    sq=_polybius_square(); out=[]
    for token in text.split():
        if token.isdigit() and len(token)==2 and token[0] in "12345" and token[1] in "12345":
            i=(int(token[0])-1)*5+int(token[1])-1; out.append(sq[i])
        else: out.append(token)
    return ''.join(out)

def bacon_encrypt(text):
    codes={ABC[i]:format(i,"05b").replace("0","a").replace("1","b") for i in range(26)}
    return " ".join(codes[c] for c in text.upper() if c in codes)

def bacon_decrypt(text):
    rev={format(i,"05b").replace("0","a").replace("1","b"):ABC[i] for i in range(26)}
    cleaned=''.join(c.lower() for c in text if c.lower() in "ab")
    return ''.join(rev.get(cleaned[i:i+5],"") for i in range(0,len(cleaned),5))

MORSE = {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.'}
MORSE_REV={v:k for k,v in MORSE.items()}
def morse_encrypt(text):
    return " ".join(MORSE.get(c.upper(), "/") if c!=" " else "/" for c in text)
def morse_decrypt(text):
    return ''.join(" " if t=="/" else MORSE_REV.get(t,"?") for t in text.split())

def columnar_encrypt(text,key):
    key=''.join(c for c in key.upper() if c.isalpha())
    if not key: raise ValueError("Keyword is required.")
    n=len(key); rows=[text[i:i+n] for i in range(0,len(text),n)]
    order=sorted(range(n), key=lambda i:(key[i],i))
    return ''.join((row[i] for i in order for row in rows if i<len(row)))

def columnar_decrypt(cipher,key):
    key=''.join(c for c in key.upper() if c.isalpha())
    if not key: raise ValueError("Keyword is required.")
    n=len(key); L=len(cipher); full, rem=divmod(L,n)
    lengths=[full+(i<rem) for i in range(n)]
    order=sorted(range(n), key=lambda i:(key[i],i))
    cols=['']*n; pos=0
    for i in order:
        cols[i]=cipher[pos:pos+lengths[i]]; pos+=lengths[i]
    return ''.join(cols[i][r] for r in range(full+1) for i in range(n) if r<len(cols[i]))

def adfgvx_encrypt(text,key):
    # Educational ADFGVX with keyed square; output uses ADFGVX symbols.
    labels="ADFGVX"; square="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    key=''.join(c for c in key.upper() if c.isalnum())
    if not key: raise ValueError("Keyword is required.")
    alphabet=''.join(dict.fromkeys(key+square))
    coords=[]
    for c in text.upper():
        if c in alphabet:
            i=alphabet.index(c); coords += [labels[i//6],labels[i%6]]
    return columnar_encrypt(''.join(coords),key)
def adfgvx_decrypt(text,key):
    labels="ADFGVX"; key=''.join(c for c in key.upper() if c.isalnum())
    if not key: raise ValueError("Keyword is required.")
    coords=columnar_decrypt(''.join(c for c in text.upper() if c in labels),key)
    square=''.join(dict.fromkeys(key+"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
    out=[]
    for i in range(0,len(coords)-1,2):
        a,b=labels.index(coords[i]),labels.index(coords[i+1]); idx=a*6+b
        if idx<len(square): out.append(square[idx])
    return ''.join(out)

def otp_encrypt(text,key):
    raw=key.encode()
    data=text.encode()
    if len(raw)<len(data): raise ValueError("One-Time Pad key must be at least as long as the text in bytes.")
    return base64.b64encode(bytes(a^b for a,b in zip(data,raw))).decode()
def otp_decrypt(text,key):
    try: data=base64.b64decode(text.encode(),validate=True)
    except Exception as e: raise ValueError("Invalid OTP ciphertext.") from e
    raw=key.encode()
    if len(raw)<len(data): raise ValueError("OTP key is too short.")
    return bytes(a^b for a,b in zip(data,raw)).decode(errors="strict")
def otp_key(length): return base64.b64encode(__import__('secrets').token_bytes(length)).decode()

def hash_text(text,algorithm):
    h=hashlib.new(algorithm); h.update(text.encode()); return h.hexdigest()

def rsa_generate(bits=512):
    # Educational RSA demo, not production cryptography.
    def prime():
        while True:
            n=__import__('secrets').randbits(bits//2)|1|(1<<(bits//2-1))
            if _is_probable_prime(n): return n
    p,q=prime(),prime()
    while q==p: q=prime()
    n=p*q; phi=(p-1)*(q-1); e=65537
    while math.gcd(e,phi)!=1: e+=2
    d=pow(e,-1,phi)
    return e,d,n
def _is_probable_prime(n,k=8):
    if n<2:return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n%p==0:return n==p
    s=0; d=n-1
    while d%2==0:s+=1;d//=2
    import secrets
    for _ in range(k):
        a=secrets.randbelow(n-3)+2; x=pow(a,d,n)
        if x in (1,n-1): continue
        for _ in range(s-1):
            x=pow(x,2,n)
            if x==n-1: break
        else:return False
    return True
def rsa_encrypt(text,e,n):
    data=text.encode(); max_len=(n.bit_length()-1)//8
    if len(data)>max_len: raise ValueError(f"Text too long for this educational RSA block. Limit: {max_len} bytes.")
    return format(pow(int.from_bytes(data,'big'),e,n),'x')
def rsa_decrypt(cipher,d,n):
    try: c=int(cipher,16)
    except ValueError as e: raise ValueError("RSA ciphertext must be hexadecimal.") from e
    m=pow(c,d,n); length=max(1,(m.bit_length()+7)//8)
    return m.to_bytes(length,'big').decode()
