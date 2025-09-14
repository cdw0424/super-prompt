"""
Personas tools (MCP-first)

CRITICAL PROTECTION: All persona tools MUST NEVER modify files in:
- .cursor/ (Cursor IDE configuration)
- .super-prompt/ (Super Prompt internal files)
- .codex/ (Codex CLI configuration)
These directories are PROTECTED and should only be modified by official installation processes.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional

from ..adapters.cursor_adapter import CursorAdapter


def personas_init_copy(project_root: Optional[Path] = None, overwrite: bool = False) -> Dict[str, Any]:
    root = Path(project_root or ".")
    src = Path(__file__).parent.parent.parent / "cursor-assets" / "manifests" / "personas.yaml"
    dst_dir = root / "personas"
    dst = dst_dir / "manifest.yaml"
    dst_dir.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        return {"ok": True, "logs": [f"➡️  personas manifest exists: {dst} (use --overwrite to replace)"]}
    dst.write_text(src.read_text())
    return {"ok": True, "logs": [f"--------personas:init: wrote manifest → {dst}"]}


def personas_build_assets(project_root: Optional[Path] = None) -> Dict[str, Any]:
    root = Path(project_root or ".")
    adapter = CursorAdapter()
    adapter.generate_commands(root)
    adapter.generate_rules(root)
    return {"ok": True, "logs": ["--------personas:build: .cursor commands + rules updated"]}

