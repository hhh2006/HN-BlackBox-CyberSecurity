"""Bacon cipher."""
ABC="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def bacon_encrypt(text):
    codes={ABC[i]:format(i,"05b").replace("0","a").replace("1","b") for i in range(26)}
    return " ".join(codes[c] for c in text.upper() if c in codes)
def bacon_decrypt(text):
    rev={format(i,"05b").replace("0","a").replace("1","b"):ABC[i] for i in range(26)}
    cleaned=''.join(c.lower() for c in text if c.lower() in "ab")
    return ''.join(rev.get(cleaned[i:i+5],"") for i in range(0,len(cleaned),5))
