"""
Super Prompt MCP Server (FastMCP)

Exposes core tools (model mode toggles, personas) over MCP (stdio).
"""

from pathlib import Path
from typing import Dict, Any
import json
import os


def _result(ok: bool, logs: list[str]) -> Dict[str, Any]:
    return {"ok": ok, "logs": logs}


def main() -> None:
    try:
        from fastmcp import FastMCP
    except Exception as e:
        # Graceful fallback if FastMCP is not installed
        print("-------- FastMCP not installed. Install with: pip install fastmcp", flush=True)
        raise SystemExit(1)

    # Lazy import to avoid CLI dependency on fastmcp when not serving
    from .. import modes as sp_modes

    app = FastMCP("super-prompt")

    def emit_event(project_root: str, etype: str, payload: Dict[str, Any]) -> None:
        try:
            store = MemoryStore.open(Path(project_root))
            store.append_event(etype, payload)
        except Exception:
            pass

    @app.tool()
    def gpt_mode_on(project_root: str = ".") -> Dict[str, Any]:
        logs = sp_modes.enable_codex_mode(Path(project_root))
        emit_event(project_root, "tool_call", {"tool": "gpt_mode_on"})
        return _result(True, logs)

    @app.tool()
    def gpt_mode_off(project_root: str = ".") -> Dict[str, Any]:
        logs = sp_modes.disable_codex_mode(Path(project_root))
        emit_event(project_root, "tool_call", {"tool": "gpt_mode_off"})
        return _result(True, logs)

    @app.tool()
    def grok_mode_on(project_root: str = ".") -> Dict[str, Any]:
        logs = sp_modes.enable_grok_mode(Path(project_root))
        emit_event(project_root, "tool_call", {"tool": "grok_mode_on"})
        return _result(True, logs)

    @app.tool()
    def grok_mode_off(project_root: str = ".") -> Dict[str, Any]:
        logs = sp_modes.disable_grok_mode(Path(project_root))
        emit_event(project_root, "tool_call", {"tool": "grok_mode_off"})
        return _result(True, logs)

    # Synonyms (optional)
    @app.tool(name="codex_mode_on")
    def codex_mode_on(project_root: str = ".") -> Dict[str, Any]:
        return gpt_mode_on(project_root)

    @app.tool(name="codex_mode_off")
    def codex_mode_off(project_root: str = ".") -> Dict[str, Any]:
        return gpt_mode_off(project_root)

    # Health check / info
    @app.tool()
    def info() -> Dict[str, Any]:
        return {
            "name": "super-prompt",
            "version": os.environ.get("SUPER_PROMPT_VERSION", "4.x"),
            "modes": ["gpt", "grok"],
        }

    # Personas/tools
    from ..commands import personas_tools as sp_personas
    from ..commands import codex_tools as sp_codex
    from ..commands import context_tools as sp_context
    from ..commands import validate_tools as sp_validate
    from ..commands import amr_tools as sp_amr
    from ..commands import amr_repo_tools as sp_amr_repo
    from ..memory.store import MemoryStore

    @app.tool()
    def personas_init(project_root: str = ".", overwrite: bool = False) -> Dict[str, Any]:
        emit_event(project_root, "tool_call", {"tool": "personas_init", "overwrite": overwrite})
        return sp_personas.personas_init_copy(Path(project_root), overwrite)

    @app.tool()
    def personas_build(project_root: str = ".") -> Dict[str, Any]:
        emit_event(project_root, "tool_call", {"tool": "personas_build"})
        return sp_personas.personas_build_assets(Path(project_root))

    @app.tool()
    def codex_init(project_root: str = ".") -> Dict[str, Any]:
        emit_event(project_root, "tool_call", {"tool": "codex_init"})
        return sp_codex.codex_init_assets(Path(project_root))

    @app.tool()
    def context_collect(project_root: str = ".", query: str = "", max_tokens: int = 16000) -> Dict[str, Any]:
        emit_event(project_root, "tool_call", {"tool": "context_collect", "q_len": len(query), "max_tokens": max_tokens})
        return sp_context.collect(Path(project_root), query, max_tokens)

    @app.tool()
    def context_stats(project_root: str = ".") -> Dict[str, Any]:
        emit_event(project_root, "tool_call", {"tool": "context_stats"})
        return sp_context.stats(Path(project_root))

    @app.tool()
    def context_clear(project_root: str = ".") -> Dict[str, Any]:
        emit_event(project_root, "tool_call", {"tool": "context_clear"})
        return sp_context.clear(Path(project_root))

    @app.tool()
    def validate_todo(task_id: str, project_root: str = ".") -> Dict[str, Any]:
        emit_event(project_root, "tool_call", {"tool": "validate_todo", "task_id": task_id})
        return sp_validate.validate_todo(task_id, Path(project_root))

    @app.tool()
    def validate_check(project_root: str = ".", target: str = "") -> Dict[str, Any]:
        emit_event(project_root, "tool_call", {"tool": "validate_check", "target": target})
        return sp_validate.validate_check(Path(project_root), target or None)

    @app.tool()
    def amr_qa(file_path: str) -> Dict[str, Any]:
        emit_event(".", "tool_call", {"tool": "amr_qa", "file": file_path})
        return sp_amr.amr_qa_file(Path(file_path))

    @app.tool()
    def amr_repo_overview(project_root: str = ".") -> Dict[str, Any]:
        emit_event(project_root, "tool_call", {"tool": "amr_repo_overview"})
        return sp_amr_repo.repo_overview(Path(project_root))

    @app.tool()
    def amr_handoff_brief(project_root: str = ".", query: str = "") -> Dict[str, Any]:
        emit_event(project_root, "tool_call", {"tool": "amr_handoff_brief", "q_len": len(query)})
        return sp_amr_repo.handoff_brief(Path(project_root), query)

    @app.tool()
    def amr_persona_orchestrate(persona: str, project_root: str = ".", query: str = "", tool_budget: int = 2) -> Dict[str, Any]:
        emit_event(project_root, "tool_call", {"tool": "amr_persona_orchestrate", "persona": persona, "q_len": len(query), "tool_budget": tool_budget})
        return sp_amr_repo.amr_persona_orchestrate(persona, Path(project_root), query, tool_budget)

    # Memory tools
    @app.tool()
    def memory_set(project_root: str = ".", key: str = "", value: str = "") -> Dict[str, Any]:
        store = MemoryStore.open(Path(project_root))
        store.set_kv(key, value)
        return {"ok": True, "logs": [f"-------- memory:set {key}"]}

    @app.tool()
    def memory_get(project_root: str = ".", key: str = "") -> Dict[str, Any]:
        store = MemoryStore.open(Path(project_root))
        val = store.get_kv(key)
        return {"ok": True, "key": key, "value": val}

    @app.tool()
    def memory_set_task(project_root: str = ".", tag: str = "") -> Dict[str, Any]:
        store = MemoryStore.open(Path(project_root))
        store.set_task_tag(tag)
        return {"ok": True, "logs": [f"-------- memory:task {tag}"]}

    @app.tool()
    def memory_get_task(project_root: str = ".") -> Dict[str, Any]:
        store = MemoryStore.open(Path(project_root))
        tag = store.get_task_tag()
        return {"ok": True, "task_tag": tag}

    @app.tool()
    def memory_append_event(project_root: str = ".", type: str = "note", payload: str = "") -> Dict[str, Any]:
        store = MemoryStore.open(Path(project_root))
        try:
            data = json.loads(payload) if payload else {}
        except Exception:
            data = {"text": payload}
        eid = store.append_event(type, data)
        return {"ok": True, "event_id": eid}

    @app.tool()
    def memory_recent(project_root: str = ".", limit: int = 20) -> Dict[str, Any]:
        store = MemoryStore.open(Path(project_root))
        ev = store.recent_events(limit)
        return {"ok": True, "events": ev}

    app.run()


if __name__ == "__main__":
    main()
