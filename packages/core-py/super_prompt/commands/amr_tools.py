"""
AMR tools (MCP-first)
"""

from pathlib import Path
from typing import Dict, Any, List
import re


def amr_qa_text(text: str) -> Dict[str, Any]:
    logs: List[str] = []
    ok = True

    if not re.search(r"^\[INTENT\]", text, re.M):
        logs.append("-------- Missing [INTENT] section"); ok = False
    if not (re.search(r"^\[PLAN\]", text, re.M) or re.search(r"^\[EXECUTE\]", text, re.M)):
        logs.append("-------- Missing [PLAN] or [EXECUTE] section"); ok = False
    if re.search(r"^(router:|run:)", text, re.M):
        logs.append("-------- Found log lines without '--------' prefix"); ok = False
    if "/model gpt-5 high" in text and "/model gpt-5 medium" not in text:
        logs.append("-------- High switch found without returning to medium"); ok = False

    logs.append("--------qa: OK" if ok else "--------qa: FAIL")
    return {"ok": ok, "logs": logs}


def amr_qa_file(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        return {"ok": False, "error": f"File not found: {file_path}", "logs": []}
    text = file_path.read_text()
    return amr_qa_text(text)

