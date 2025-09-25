"""Super Prompt Core Library v5.6.5 with safe memory fallback."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from threading import Lock
from types import ModuleType
from typing import Any, Dict, List, Optional

__version__ = "5.6.5"
__all__ = ["engine", "context", "sdd", "personas", "adapters", "validation"]

_PKG_ROOT = Path(__file__).resolve().parent
_MEMORY_STORE_PATH = _PKG_ROOT / "memory" / "store.py"


def _register_memory_fallback() -> None:
    """Register an in-memory fallback for `super_prompt.memory` when missing."""

    class _InMemoryStore:
        """Lightweight in-process stand-in when the real SQLite-backed store is absent."""

        def __init__(self) -> None:
            self.path = Path(":memory:")
            self._kv: Dict[str, Any] = {}
            self._sessions: Dict[int, float] = {}
            self._events: List[Dict[str, Any]] = []
            self._next_session_id = 1
            self._next_event_id = 1

        def _ensure_session(self, session_id: Optional[int]) -> int:
            if session_id is not None and session_id in self._sessions:
                return session_id

            sid = session_id or self._next_session_id
            if sid not in self._sessions:
                self._sessions[sid] = time.time()
                self._next_session_id = max(self._next_session_id, sid + 1)
            return sid

        # Public API -----------------------------------------------------------------
        @classmethod
        def open(cls, project_root: Optional[Path] = None) -> "_InMemoryStore":
            del project_root  # Unused but kept for signature compatibility
            with _STORE_LOCK:
                if _STORE_SINGLETON[0] is None:
                    _STORE_SINGLETON[0] = cls()
                return _STORE_SINGLETON[0]

        def set_kv(self, key: str, value: Any) -> None:
            self._kv[key] = value

        def get_kv(self, key: str) -> Optional[Any]:
            return self._kv.get(key)

        def new_session(self) -> int:
            sid = self._ensure_session(None)
            return sid

        def append_event(
            self,
            event_type: str,
            payload: Dict[str, Any],
            session_id: Optional[int] = None,
        ) -> int:
            sid = self._ensure_session(session_id)
            event = {
                "id": self._next_event_id,
                "session_id": sid,
                "ts": time.time(),
                "type": event_type,
                "payload": payload,
            }
            self._events.append(event)
            self._next_event_id += 1
            return event["id"]

        def recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
            return list(reversed(self._events[-limit:]))

        def set_task_tag(self, tag: str) -> None:
            self.set_kv("task_tag", tag)

        def get_task_tag(self) -> Optional[str]:
            value = self.get_kv("task_tag")
            return str(value) if value is not None else None

    # Create module placeholders so `from ...memory.store import MemoryStore` works.
    memory_module = ModuleType("super_prompt.memory")
    store_module = ModuleType("super_prompt.memory.store")

    memory_module.__path__ = []  # Mark as namespace-like for import machinery
    memory_module.MemoryStore = _InMemoryStore
    memory_module.store = store_module

    store_module.MemoryStore = _InMemoryStore

    sys.modules.setdefault("super_prompt.memory", memory_module)
    sys.modules.setdefault("super_prompt.memory.store", store_module)


_STORE_LOCK = Lock()
_STORE_SINGLETON: List[Optional[object]] = [None]

if not _MEMORY_STORE_PATH.exists():
    _register_memory_fallback()
