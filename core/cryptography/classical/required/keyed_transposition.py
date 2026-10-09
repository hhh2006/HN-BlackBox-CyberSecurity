"""Keyed Transposition / columnar transposition engine."""

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
