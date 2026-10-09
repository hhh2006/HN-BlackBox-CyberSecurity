# -*- coding: utf-8 -*-
"""Safe local history storage for HN BlackBox."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

MAX_ENTRIES = 200


def _default_path() -> Path:
    """Return a user-writable location instead of the application folder."""
    if os.name == "nt":
        root = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA")
        base = Path(root) if root else Path.home() / "AppData" / "Roaming"
    elif os.name == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "HN BlackBox" / "history.json"


DEFAULT_PATH = str(_default_path())


def _load(path: str = DEFAULT_PATH) -> list[dict]:
    try:
        file_path = Path(path)
        if not file_path.is_file():
            return []
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError, TypeError):
        return []


def _save(entries: list[dict], path: str = DEFAULT_PATH) -> None:
    file_path = Path(path)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
        temp_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(file_path)
    except OSError:
        # History must never break the encryption workflow if the storage
        # location becomes unavailable or read-only.
        return


def _safe_key_display(value: str) -> str:
    """Prevent the local audit trail from becoming a plaintext key vault."""
    text = str(value or "")
    if not text:
        return ""
    # Preserve a little context for operators without persisting secret material.
    if len(text) <= 4:
        return "••••"
    return text[:2] + "••••" + text[-2:]


def add_entry(
    algorithm: str,
    operation: str,
    key_display: str,
    input_text: str,
    output_text: str,
    path: str = DEFAULT_PATH,
) -> None:
    entries = _load(path)
    entries.insert(
        0,
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "algorithm": algorithm,
            "operation": operation,
            "key": _safe_key_display(key_display),
            "input": input_text,
            "output": output_text,
        },
    )
    _save(entries[:MAX_ENTRIES], path)


def get_all(path: str = DEFAULT_PATH) -> list[dict]:
    return _load(path)


def clear(path: str = DEFAULT_PATH) -> None:
    _save([], path)
