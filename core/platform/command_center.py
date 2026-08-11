"""Command Center snapshot aggregating existing and new local subsystems."""
from __future__ import annotations
from datetime import datetime
from ..security_labs import labs2

def snapshot(module_count=0, history_count=0):
    lab=labs2.score()
    return {"generated_at":datetime.now().isoformat(timespec="seconds"),"modules":module_count,"history":history_count,"labs":lab,"state":"LOCAL / READY"}
