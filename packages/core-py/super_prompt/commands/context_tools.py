"""
Context collection tools (MCP-first)
"""

from pathlib import Path
from typing import Dict, Any, Optional

from ..context.collector import ContextCollector


def collect(project_root: Optional[Path], query: str, max_tokens: int = 16000) -> Dict[str, Any]:
    root = str(project_root) if project_root else "."
    collector = ContextCollector(root)
    result = collector.collect_context(query, max_tokens=max_tokens)
    logs = [
        f"📊 Collected context for: {query}",
        f"   Files: {len(result['files'])}",
        f"   Tokens: {result['metadata']['context_tokens']}",
        f"   Time: {result['metadata']['collection_time']:.2f}s",
    ]
    return {"ok": True, "logs": logs, "result": result}


def stats(project_root: Optional[Path]) -> Dict[str, Any]:
    root = str(project_root) if project_root else "."
    collector = ContextCollector(root)
    s = collector.get_stats()
    logs = [
        "Context collector stats:",
        f"   Cache size: {s['cache_size']}",
        f"   Gitignore loaded: {s['gitignore_loaded']}",
    ]
    return {"ok": True, "logs": logs, "stats": s}


def clear(project_root: Optional[Path]) -> Dict[str, Any]:
    root = str(project_root) if project_root else "."
    collector = ContextCollector(root)
    collector.clear_cache()
    return {"ok": True, "logs": ["✅ Context cache cleared"]}

