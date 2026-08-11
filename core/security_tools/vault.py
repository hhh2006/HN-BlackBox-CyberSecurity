from __future__ import annotations
import base64, json, os
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def _key(password,salt):
    kdf=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=390000)
    return kdf.derive(password.encode('utf-8'))

def seal(data,password,path):
    salt=os.urandom(16); nonce=os.urandom(12); key=_key(password,salt)
    raw=json.dumps(data,ensure_ascii=False).encode(); ct=AESGCM(key).encrypt(nonce,raw,None)
    Path(path).write_text(json.dumps({'v':1,'salt':base64.b64encode(salt).decode(),'nonce':base64.b64encode(nonce).decode(),'data':base64.b64encode(ct).decode()}),encoding='utf-8')

def open_vault(password,path):
    obj=json.loads(Path(path).read_text(encoding='utf-8')); salt=base64.b64decode(obj['salt']); nonce=base64.b64decode(obj['nonce']); ct=base64.b64decode(obj['data'])
    raw=AESGCM(_key(password,salt)).decrypt(nonce,ct,None); return json.loads(raw.decode('utf-8'))
