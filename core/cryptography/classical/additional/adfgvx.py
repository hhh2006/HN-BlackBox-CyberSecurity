"""Educational ADFGVX cipher with keyed transposition."""
from core.cryptography.classical.required.keyed_transposition import columnar_encrypt, columnar_decrypt
def adfgvx_encrypt(text,key):
    labels="ADFGVX"; square="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"; key=''.join(c for c in key.upper() if c.isalnum())
    if not key: raise ValueError("Keyword is required.")
    alphabet=''.join(dict.fromkeys(key+square)); coords=[]
    for c in text.upper():
        if c in alphabet:
            i=alphabet.index(c); coords += [labels[i//6],labels[i%6]]
    return columnar_encrypt(''.join(coords),key)
def adfgvx_decrypt(text,key):
    labels="ADFGVX"; key=''.join(c for c in key.upper() if c.isalnum())
    if not key: raise ValueError("Keyword is required.")
    coords=columnar_decrypt(''.join(c for c in text.upper() if c in labels),key); square=''.join(dict.fromkeys(key+"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")); out=[]
    for i in range(0,len(coords)-1,2):
        a,b=labels.index(coords[i]),labels.index(coords[i+1]); idx=a*6+b
        if idx<len(square): out.append(square[idx])
    return ''.join(out)
