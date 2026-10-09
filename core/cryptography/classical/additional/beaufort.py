"""Beaufort cipher."""
ABC="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def beaufort(text,key):
    key=''.join(c for c in key.upper() if c in ABC)
    if not key: raise ValueError("Keyword is required.")
    out=[]; j=0
    for c in text:
        if c.upper() in ABC:
            x=ABC.index(c.upper()); k=ABC.index(key[j%len(key)]); y=(k-x)%26; out.append(ABC[y] if c.isupper() else ABC[y].lower()); j+=1
        else: out.append(c)
    return ''.join(out)
