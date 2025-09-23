"""High reasoning mode toggle storage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .paths import project_data_dir

_HIGH_MODE_FILE = project_data_dir() / "high-mode.json"


def _read_payload() -> dict:
    if not _HIGH_MODE_FILE.exists():
        return {}
    try:
        return json.loads(_HIGH_MODE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def is_high_mode_enabled(default: bool = False) -> bool:
    payload = _read_payload()
    value = payload.get("enabled")
    if isinstance(value, bool):
        return value
    return bool(default)


def set_high_mode(enabled: bool) -> bool:
    _HIGH_MODE_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {"enabled": bool(enabled)}
    _HIGH_MODE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload["enabled"]


def high_mode_path() -> Path:
    return _HIGH_MODE_FILE
