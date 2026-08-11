"""Persistent local progress for HN BlackBox offline labs."""
from __future__ import annotations
import json, os
from pathlib import Path

def _path() -> Path:
    if os.name == "nt": base=Path(os.environ.get("APPDATA") or Path.home()/"AppData"/"Roaming")
    elif os.name == "darwin": base=Path.home()/"Library"/"Application Support"
    else: base=Path(os.environ.get("XDG_DATA_HOME",Path.home()/".local"/"share"))
    return base/"HN BlackBox"/"lab_progress.json"

def _clean(data):
    if not isinstance(data,dict): data={}
    return {"completed":sorted(set(map(str,data.get("completed",[])))),"attempts":{str(k):max(0,int(v)) for k,v in (data.get("attempts") or {}).items() if str(k)}}

def get_progress():
    try:
        p=_path()
        if p.is_file(): return _clean(json.loads(p.read_text(encoding="utf-8")))
    except Exception: pass
    return {"completed":[],"attempts":{}}

def save(data):
    data=_clean(data); p=_path()
    try:
        p.parent.mkdir(parents=True,exist_ok=True); tmp=p.with_suffix(".tmp"); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8"); tmp.replace(p)
    except OSError: pass

def record_attempt(lab_id, correct=False):
    d=get_progress(); k=str(lab_id); d["attempts"][k]=d["attempts"].get(k,0)+1
    if correct and k not in d["completed"]: d["completed"].append(k)
    save(d); return d

def reset(): save({"completed":[],"attempts":{}})

def import_progress(data): save(data or {})
