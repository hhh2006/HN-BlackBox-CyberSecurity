"""Reusable local diagnostics for the HN BlackBox GUI."""
from __future__ import annotations
import importlib, platform, sys
from pathlib import Path

def run(root: Path, history_path: str, psutil_available: bool):
    rows=[]; ok=True
    def add(label, passed, detail=""):
        nonlocal ok; ok=ok and bool(passed); rows.append((bool(passed),label,detail))
    add("Python runtime",sys.version_info >= (3,9),platform.python_version())
    try:
        import tkinter as tk; add("Tkinter",tk.TkVersion >= 8.6,str(tk.TkVersion))
    except Exception as exc: add("Tkinter",False,str(exc))
    add("Core package",(root/"core").is_dir(),str(root/"core")); add("GUI package",(root/"gui").is_dir(),str(root/"gui")); add("History storage",True,history_path); add("psutil optional",True,"available" if psutil_available else "optional / not installed")
    for name in ("caesar","vigenere","cryptanalysis","network_tools","web_lab","blue_team","labs","lab_progress","reporting"):
        try: importlib.import_module("core."+name); add("Core import "+name,True,"loaded")
        except Exception as exc: add("Core import "+name,False,str(exc)[:100])
    return ok,rows
