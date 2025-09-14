"""
Codex assets tools (MCP-first)
"""

from pathlib import Path
from typing import Dict, Any, Optional

from ..adapters.codex_adapter import CodexAdapter


def codex_init_assets(project_root: Optional[Path] = None) -> Dict[str, Any]:
    root = Path(project_root or ".")
    adapter = CodexAdapter()
    adapter.generate_assets(root)
    return {"ok": True, "logs": ["--------codex:init: .codex assets created"]}

