"""Atbash substitution cipher."""
ABC="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def atbash(text: str) -> str:
    out=[]
    for c in text:
        if c.upper() in ABC:
            a=ABC if c.isupper() else ABC.lower(); out.append(a[25-a.index(c)])
        else: out.append(c)
    return "".join(out)
