"""Local integrity and safe-input helpers."""
from __future__ import annotations
import hashlib, json, secrets
from pathlib import Path

def file_sha256(path):
    h=hashlib.sha256();
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def safe_json_write(path,data):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); tmp=p.with_suffix(p.suffix+".tmp"); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8"); tmp.replace(p)

def random_id(prefix="case"): return prefix+"-"+secrets.token_hex(6)
