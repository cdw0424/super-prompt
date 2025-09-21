"""
Validation tools (MCP-first)
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from ..sdd.gates import check_implementation_ready
from ..context.collector import ContextCollector
from ..validation.todo_validator import TodoValidator


def validate_todo(task_id: str, project_root: Optional[Path] = None) -> Dict[str, Any]:
    v = TodoValidator()
    ok, msg = v.validate_task_completion(task_id)
    logs: List[str] = []
    if ok:
        logs.append(f"✅ Task '{task_id}' validation passed")
    else:
        logs.append(f"❌ Task '{task_id}' validation failed: {msg}")
    return {"ok": ok, "logs": logs}


def validate_check(
    project_root: Optional[Path] = None, target: Optional[str] = None
) -> Dict[str, Any]:
    root = str(project_root) if project_root else "."
    logs: List[str] = ["Running validation checks:"]
    all_passed = True

    def log_status(name: str, passed: bool, details: str = ""):
        nonlocal all_passed
        status = "✅" if passed else "❌"
        logs.append(f"   {status} {name}{details}")
        if not passed:
            all_passed = False

    try:
        sdd_ok = check_implementation_ready(target or "default", root)
        passed = sdd_ok.ok if hasattr(sdd_ok, "ok") else bool(sdd_ok)
        details = (
            f" ({len(sdd_ok.missing)} issues)"
            if hasattr(sdd_ok, "missing") and sdd_ok.missing
            else ""
        )
        log_status("SDD gates", passed, details)
    except Exception as e:
        log_status("SDD gates", False, f" (error: {e})")

    try:
        ctx = ContextCollector(root)
        count = len(ctx.collect_context("test")["files"]) > 0
        log_status("Context collection", bool(count))
    except Exception as e:
        log_status("Context collection", False, f" (error: {e})")

    if all_passed:
        logs.append("🎉 All validation checks passed!")
    else:
        logs.append("⚠️  Some validation checks failed")

    return {"ok": all_passed, "logs": logs}
