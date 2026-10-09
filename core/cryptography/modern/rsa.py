"""Educational RSA demonstration engine."""
import math, secrets
def rsa_generate(bits=512):
    def prime():
        while True:
            n=secrets.randbits(bits//2)|1|(1<<(bits//2-1))
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
