"""
AMR repository insight tools (MCP-first)

Lightweight, non-LLM analysis to help a smaller model assemble a concise
handoff brief for a higher-reasoning model.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
import json
import re


def _detect_languages(root: Path) -> Dict[str, int]:
    exts = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".cs": "csharp",
        ".rb": "ruby",
        ".php": "php",
        ".sh": "shell",
        ".md": "markdown",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".toml": "toml",
        ".json": "json",
    }
    counts: Dict[str, int] = {}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(seg in p.parts for seg in [".git", "node_modules", ".venv", "venv", "dist", "build", ".turbo", ".next", ".parcel-cache"]):
            continue
        lang = exts.get(p.suffix.lower())
        if not lang:
            continue
        counts[lang] = counts.get(lang, 0) + 1
    return counts


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text()) if path.exists() else {}
    except Exception:
        return {}


def _detect_frameworks(root: Path) -> List[str]:
    hints: List[str] = []
    pkg = _read_json(root / "package.json")
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    for key in deps.keys():
        k = key.lower()
        if k in ("react", "next", "vite", "svelte", "vue", "nuxt"):
            hints.append(k)
        if k in ("jest", "vitest", "mocha", "cypress"):
            hints.append(k)
        if k in ("express", "koa", "fastify"):
            hints.append(k)

    pyproject = root / "packages" / "core-py" / "pyproject.toml"
    if pyproject.exists():
        hints.append("pyproject")

    # Heuristics for frameworks
    if (root / "manage.py").exists():
        hints.append("django")
    if (root / "requirements.txt").exists():
        txt = (root / "requirements.txt").read_text().lower()
        if "fastapi" in txt:
            hints.append("fastapi")

    return sorted(set(hints))


def _find_tests(root: Path) -> List[str]:
    tests: List[str] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(seg in p.parts for seg in [".git", "node_modules", ".venv", "venv", "dist", "build"]):
            continue
        name = p.name.lower()
        if name.endswith((".test.js", ".test.ts", ".spec.js", ".spec.ts", ".int.test.js")) or name.startswith(("test_",)) or "/test" in "/".join(p.parts).lower() or "/tests" in "/".join(p.parts).lower():
            tests.append(str(p.relative_to(root)))
    return tests[:50]


def repo_overview(project_root: Path) -> Dict[str, Any]:
    root = Path(project_root or ".").resolve()
    langs = _detect_languages(root)
    frameworks = _detect_frameworks(root)
    tests = _find_tests(root)

    top_dirs = [p.name for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")][:20]
    files_important = []
    for p in ["README.md", "AGENTS.md", ".cursor/rules", ".cursor/commands", "packages/core-py/super_prompt/cli.py", "src/prompts/codexAmrBootstrap.en.js"]:
        q = root / p
        if q.exists():
            files_important.append(p)

    return {
        "root": str(root),
        "languages": langs,
        "frameworks": frameworks,
        "top_dirs": top_dirs,
        "tests_sample": tests,
        "important": files_important,
    }


def handoff_brief(project_root: Path, query: str) -> Dict[str, Any]:
    info = repo_overview(project_root)
    langs = ", ".join(f"{k}:{v}" for k, v in sorted(info["languages"].items(), key=lambda x: -x[1])) or "n/a"
    frameworks = ", ".join(info["frameworks"]) or "n/a"
    tests = ", ".join(info["tests_sample"][:10]) or "n/a"
    important = ", ".join(info["important"]) or "n/a"

    brief = f"""
[AMR HANDOFF BRIEF]
- Task: {query}
- Languages(files): {langs}
- Frameworks/signals: {frameworks}
- Important files: {important}
- Tests sample: {tests}
- Project root: {info['root']}

[CONTEXT NOTES]
- Use repo map above to infer relevant modules.
- Prioritize minimal diffs and existing conventions.
- If execution requires heavy reasoning, execute at gpt-5 high; otherwise medium.
""".strip()

    return {"ok": True, "brief": brief, "overview": info}


def amr_persona_orchestrate(persona: str, project_root: Path, query: str, tool_budget: int = 2) -> Dict[str, Any]:
    """One-shot AMR helper for personas.

    Returns a compact overview + handoff brief and a suggested next-step plan
    that callers (IDE/agent) can follow. This keeps personas pure while
    centralizing MCP usage here.
    """
    ov = repo_overview(project_root)
    hb = handoff_brief(project_root, query)

    # Memory integration: load task tag and include in brief
    try:
        from ..memory.store import MemoryStore
        store = MemoryStore.open(project_root)
        task_tag = store.get_task_tag()
    except Exception:
        task_tag = None

    # Simple escalation heuristic based on query keywords
    ql = (query or "").lower()
    heavy_keywords = ["architecture", "design", "refactor", "root cause", "security", "performance", "deep"]
    escalate = any(k in ql for k in heavy_keywords)

    suggested = [
        {
            "step": "analyze_repo",
            "tool": "amr_repo_overview",
            "status": "done",
        },
        {
            "step": "create_handoff_brief",
            "tool": "amr_handoff_brief",
            "status": "done",
        },
    ]
    if escalate:
        suggested.append({
            "step": "escalate_reasoning",
            "command": "/model gpt-5 high",
            "status": "pending",
        })
        suggested.append({
            "step": "execute_high",
            "note": "Perform heavy reasoning/execution, then return to medium",
            "status": "pending",
        })
        suggested.append({
            "step": "return_medium",
            "command": "/model gpt-5 medium",
            "status": "pending",
        })
    else:
        suggested.append({
            "step": "execute_medium",
            "note": "Proceed at medium reasoning",
            "status": "pending",
        })

    # Persona-specific suggested tools
    p = (persona or "").lower()
    if p in ("frontend", "backend", "dev", "architect"):
        suggested.append({"step": "collect_context", "tool": "context_collect", "status": "pending"})
    if p in ("security",):
        suggested.append({"step": "validate", "tool": "validate_check", "status": "pending"})
    if p in ("qa",):
        suggested.append({"step": "qa_check", "tool": "validate_check", "status": "pending"})
    if p in ("performance",):
        suggested.append({"step": "perf_context", "tool": "context_collect", "status": "pending"})

    return {
        "ok": True,
        "persona": persona,
        "tool_budget": tool_budget,
        "overview": ov.get("overview") if isinstance(ov, dict) else ov,
        "brief": hb.get("brief") if isinstance(hb, dict) else hb,
        "task_tag": task_tag,
        "suggested_next": suggested,
    }
