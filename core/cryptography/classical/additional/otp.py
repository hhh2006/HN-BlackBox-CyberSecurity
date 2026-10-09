"""One-Time Pad educational utility."""
import base64, secrets
def otp_encrypt(text,key):
    raw=key.encode(); data=text.encode()
    if len(raw)<len(data): raise ValueError("One-Time Pad key must be at least as long as the text in bytes.")
    return base64.b64encode(bytes(a^b for a,b in zip(data,raw))).decode()
def otp_decrypt(text,key):
    try: data=base64.b64decode(text.encode(),validate=True)
    except Exception as e: raise ValueError("Invalid OTP ciphertext.") from e
    raw=key.encode()
    if len(raw)<len(data): raise ValueError("OTP key is too short.")
    return bytes(a^b for a,b in zip(data,raw)).decode(errors="strict")
def otp_key(length): return base64.b64encode(secrets.token_bytes(length)).decode()
