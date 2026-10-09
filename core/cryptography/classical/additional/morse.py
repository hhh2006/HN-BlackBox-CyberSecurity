"""Morse code."""
MORSE={'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.'}
MORSE_REV={v:k for k,v in MORSE.items()}
def morse_encrypt(text): return " ".join(MORSE.get(c.upper(), "/") if c!=" " else "/" for c in text)
def morse_decrypt(text): return ''.join(" " if t=="/" else MORSE_REV.get(t,"?") for t in text.split())
