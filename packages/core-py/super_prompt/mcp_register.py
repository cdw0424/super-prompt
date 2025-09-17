from __future__ import annotations

import json
import os
from pathlib import Path


def _render_codex_config_block(project_root: Path,
                               server_name: str,
                               npm_spec: str,
                               python_exec: str) -> str:
    """Render canonical Codex MCP config block for super:init."""
    project_path = str(project_root).replace("\\", "\\\\").replace('"', '\\"')
    python_exec = python_exec or "python3"
    env_entries = [
        'SUPER_PROMPT_ALLOW_INIT = "true"',
        f'SUPER_PROMPT_PROJECT_ROOT = "{project_path}"',
        f'PYTHON = "{python_exec}"',
    ]
    env_inline = ", ".join(env_entries)
    return (
        f"[mcp_servers.{server_name}]\n"
        'command = "npx"\n'
        f'args = ["-y", "{npm_spec}", "sp-mcp"]\n'
        f"env = {{ {env_inline} }}\n"
    )


def _ensure_codex_web_search_enabled(body: str) -> str:
    lines = body.splitlines()
    tools_idx = None
    for idx, line in enumerate(lines):
        if line.strip() == "[tools]":
            tools_idx = idx
            break

    if tools_idx is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append("[tools]")
        lines.append("web_search = true")
    else:
        end_idx = len(lines)
        for i in range(tools_idx + 1, len(lines)):
            stripped = lines[i].strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                end_idx = i
                break

        web_idx = None
        for i in range(tools_idx + 1, end_idx):
            stripped = lines[i].strip()
            if stripped.startswith("web_search"):
                leading_ws = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
                lines[i] = f"{leading_ws}web_search = true"
                web_idx = i
                break

        if web_idx is None:
            lines.insert(end_idx, "web_search = true")

    body = "\n".join(lines)
    if body and not body.endswith("\n"):
        body += "\n"
    return body

def ensure_cursor_mcp_registered(project_root: Path,
                                 npm_spec: str | None = None,
                                 server_name: str = "super-prompt") -> Path:
    """
    프로젝트 전용 .cursor/mcp.json에 MCP 서버 등록/갱신.
    기존 설정은 보존하여 병합합니다.
    """
    cursor_dir = project_root / ".cursor"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = cursor_dir / "mcp.json"

    # npx가 실행할 패키지 스펙(정확한 설치버전 우선, 없으면 latest)
    npm_spec = npm_spec or os.environ.get("SUPER_PROMPT_NPM_SPEC") or "@cdw0424/super-prompt@latest"

    entry = {
        "command": "npx",
        "args": ["-y", npm_spec, "sp-mcp"],
        "env": {
            # 설치/갱신을 MCP에서 허용(보안상 프로젝트 스코프에서만)
            "SUPER_PROMPT_ALLOW_INIT": "true",
            # 서버가 프로젝트 루트를 정확히 인식하도록 전달
            "SUPER_PROMPT_PROJECT_ROOT": str(project_root),
            # 파이썬 선택(없으면 python3)
            "PYTHON": os.environ.get("PYTHON", "python3")
        }
    }

    data = {}
    if cfg_path.exists():
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8") or "{}")
        except Exception:
            # 파손/비JSON이면 보수적으로 새로 작성
            data = {}

    mcp = data.get("mcpServers") or {}
    # 이미 있으면 업데이트(명령/args/env만 갱신), 없으면 추가
    if server_name in mcp and isinstance(mcp[server_name], dict):
        merged = dict(mcp[server_name])
        merged.update(entry)
        # env는 얕은 병합
        merged_env = dict(mcp[server_name].get("env") or {})
        merged_env.update(entry["env"])
        merged["env"] = merged_env
        mcp[server_name] = merged
    else:
        mcp[server_name] = entry

    data["mcpServers"] = mcp
    cfg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return cfg_path

def ensure_codex_mcp_registered(project_root: Path,
                                server_name: str = "super-prompt",
                                overwrite: bool = False) -> Path:
    # ~/.codex/config.toml 갱신 (overwrite=True 시 완전 재작성)
    home = Path(os.environ.get("HOME") or "~").expanduser()
    codex_dir = Path(os.environ.get("CODEX_HOME") or (home / ".codex"))
    codex_dir.mkdir(parents=True, exist_ok=True)
    cfg = codex_dir / "config.toml"

    npm_spec = os.environ.get("SUPER_PROMPT_NPM_SPEC") or "@cdw0424/super-prompt@latest"
    python_exec = os.environ.get("PYTHON", "python3")
    block = _render_codex_config_block(project_root, server_name, npm_spec, python_exec)

    if overwrite or not cfg.exists():
        body = block
    else:
        body = cfg.read_text(encoding="utf-8")
        header = f"[mcp_servers.{server_name}]"
        if header in body:
            start_idx = body.index(header)
            search_start = start_idx + len(header)
            next_idx = body.find("\n[", search_start)
            end_idx = next_idx if next_idx != -1 else len(body)
            body = body[:start_idx] + block + body[end_idx:]
        else:
            if body and not body.endswith("\n"):
                body += "\n"
            body += block

    body = _ensure_codex_web_search_enabled(body)
    if body and not body.endswith("\n"):
        body += "\n"
    cfg.write_text(body, encoding="utf-8")
    return cfg
