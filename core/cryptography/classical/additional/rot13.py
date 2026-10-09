"""ROT13 substitution cipher."""
ABC="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def _shift_char(ch,k):
    if ch.isalpha() and ch.upper() in ABC:
        alpha=ABC if ch.isupper() else ABC.lower(); return alpha[(alpha.index(ch)+k)%26]
    return ch
def rot13(text: str) -> str: return ''.join(_shift_char(c,13) for c in text)
