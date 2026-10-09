"""Polybius square."""
def _polybius_square(): return "ABCDEFGHIKLMNOPQRSTUVWXYZ"
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
