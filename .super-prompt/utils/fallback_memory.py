#!/usr/bin/env python3
"""
SQLite fallback MemoryController for packaged installs.
Stores to ./memory/ltm.db with a minimal schema.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional
import json, time, uuid, sqlite3


class MemoryController:
    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = Path(project_root or ".").resolve()
        self.memory_dir = self._resolve_memory_dir()
        self.db_path = self.memory_dir / "ltm.db"
        self.conn: Optional[sqlite3.Connection] = None
        self._ensure_db()

    def _resolve_memory_dir(self) -> Path:
        """Resolve memory directory, preferring venv/data if available."""
        # Try .super-prompt/venv/data first (preferred)
        venv_data_dir = self.project_root / ".super-prompt" / "venv" / "data"
        if venv_data_dir.exists():
            return venv_data_dir / "memory"

        # Fallback to traditional memory directory
        return self.project_root / "memory"

    def _ensure_db(self) -> sqlite3.Connection:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
        cur = self.conn.cursor()
        # Projects table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS project(
              id INTEGER PRIMARY KEY,
              code TEXT NOT NULL UNIQUE,
              name TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        # Generic memory table (facts, messages, etc.)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS memory(
              id INTEGER PRIMARY KEY,
              project_id INTEGER NOT NULL,
              kind TEXT NOT NULL,
              source TEXT,
              author TEXT,
              title TEXT,
              body TEXT NOT NULL,
              tags TEXT,
              importance REAL NOT NULL DEFAULT 0,
              pinned INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES project(id)
            );
            """
        )
        self.conn.commit()
        return self.conn

    def _ensure_project(self) -> int:
        code = self.project_root.name or "default"
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM project WHERE code=?", (code,))
        row = cur.fetchone()
        if row:
            return int(row[0])
        cur.execute("INSERT INTO project(code, name) VALUES(?,?)", (code, code))
        self.conn.commit()
        return int(cur.lastrowid)

    def build_context_block(self) -> str:
        pid = self._ensure_project()
        cur = self.conn.cursor()
        cur.execute(
            "SELECT author, body FROM memory WHERE project_id=? AND kind='message' ORDER BY id DESC LIMIT 8",
            (pid,)
        )
        rows = cur.fetchall() or []
        hist = [{"role": ("user" if r[0]=="user" else "assistant"), "content": r[1]} for r in rows][::-1]
        preview = {
            "session_info": {"session_id": str(uuid.uuid4()), "language_code": "en-US", "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
            "user_profile": {"user_id": "anonymous", "name": "Anonymous", "preferences": {"tone": "friendly", "detail_level": "concise"}},
            "active_state": {"active_conditions": [], "short_term_memory": (hist[-1]["content"] if hist else "")[:256]},
            "core_memory": {"key_memories": []},
            "recent_chat": hist,
        }
        return json.dumps(preview, ensure_ascii=False, indent=2)

    def append_interaction(self, user_text: str, assistant_text: Optional[str]) -> None:
        """Append a user/assistant exchange into the generic memory table.
        Keeps schema minimal and compatible with build_context_block().
        """
        if not assistant_text:
            return
        conn = self._ensure_db()
        pid = self._ensure_project()
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        cur = conn.cursor()
        # Store user message
        cur.execute(
            """
            INSERT INTO memory(project_id, kind, source, author, title, body, tags, importance, pinned, created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (pid, 'message', 'cli', 'user', (user_text or '')[:80], user_text or '', 'chat', 0.0, 0, now)
        )
        # Store assistant reply
        cur.execute(
            """
            INSERT INTO memory(project_id, kind, source, author, title, body, tags, importance, pinned, created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (pid, 'message', 'cli', 'assistant', (assistant_text or '')[:80], assistant_text or '', 'chat', 0.0, 0, now)
        )
        conn.commit()

    def update_from_extraction(self, extracted: Dict[str, Any]) -> None:
        if not extracted:
            return
        pid = self._ensure_project()
        cur = self.conn.cursor()
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        # Store key facts as 'fact'
        for s in (extracted.get('key_memories') or []):
            if isinstance(s, str) and s:
                cur.execute(
                    "INSERT INTO memory(project_id, kind, source, author, title, body, tags, importance, pinned, created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (pid, 'fact', 'extraction', 'system', s[:80], s, 'fact,extraction', 0.3, 0, now)
                )
        self.conn.commit()
