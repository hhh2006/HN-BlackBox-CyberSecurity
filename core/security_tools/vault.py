from __future__ import annotations
import base64, json, os
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def _key(password,salt):
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("Vault password must be at least 8 characters.")
    kdf=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=390000)
    return kdf.derive(password.encode('utf-8'))

def seal(data,password,path):
    salt=os.urandom(16); nonce=os.urandom(12); key=_key(password,salt)
    raw=json.dumps(data,ensure_ascii=False).encode(); ct=AESGCM(key).encrypt(nonce,raw,None)
    payload=json.dumps({'v':1,'salt':base64.b64encode(salt).decode(),'nonce':base64.b64encode(nonce).decode(),'data':base64.b64encode(ct).decode()}, separators=(',', ':'))
    target=Path(path); target.parent.mkdir(parents=True, exist_ok=True); tmp=target.with_suffix(target.suffix+'.tmp')
    tmp.write_text(payload, encoding='utf-8'); tmp.replace(target)

def open_vault(password,path):
    obj=json.loads(Path(path).read_text(encoding='utf-8'));
    if obj.get('v') != 1: raise ValueError('Unsupported vault format.')
    try:
        salt=base64.b64decode(obj['salt'], validate=True); nonce=base64.b64decode(obj['nonce'], validate=True); ct=base64.b64decode(obj['data'], validate=True)
    except Exception as exc:
        raise ValueError('Vault data is corrupt.') from exc
    if len(salt) != 16 or len(nonce) != 12 or len(ct) < 16: raise ValueError('Vault data is corrupt.')
    raw=AESGCM(_key(password,salt)).decrypt(nonce,ct,None); return json.loads(raw.decode('utf-8'))
