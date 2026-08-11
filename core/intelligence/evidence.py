"""Evidence registry with integrity hashing; file contents are never copied."""
from __future__ import annotations
import hashlib, os
from pathlib import Path
from datetime import datetime

def hash_file(path, algorithm="sha256", chunk=1024*1024):
    h=hashlib.new(algorithm)
    with open(path,"rb") as f:
        while True:
            b=f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

def inspect(path):
    p=Path(path)
    return {"path":str(p),"name":p.name,"exists":p.is_file(),"size":p.stat().st_size if p.is_file() else 0,"sha256":hash_file(p) if p.is_file() else "","captured_at":datetime.now().isoformat(timespec="seconds")}

def verify(item):
    return bool(item.get("exists") and Path(item.get("path","")).is_file() and hash_file(item["path"])==item.get("sha256"))
