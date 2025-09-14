from __future__ import annotations
import json, os
from pathlib import Path

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
                                server_name: str = "super-prompt") -> Path:
    # ~/.codex/config.toml 병합 ([mcp_servers.<name>])
    home = Path(os.environ.get("HOME") or "~").expanduser()
    codex_dir = Path(os.environ.get("CODEX_HOME") or (home / ".codex"))
    codex_dir.mkdir(parents=True, exist_ok=True)
    cfg = codex_dir / "config.toml"

    npm_spec = os.environ.get("SUPER_PROMPT_NPM_SPEC") or "@cdw0424/super-prompt@latest"
    block = (
        f"[mcp_servers.{server_name}]\n"
        f'command = "npx"\n'
        f'args = ["-y", "{npm_spec}", "sp-mcp"]\n'
        f'env = {{"SUPER_PROMPT_ALLOW_INIT" = "true", "SUPER_PROMPT_PROJECT_ROOT" = "{str(project_root)}", "PYTHON" = "{os.environ.get("PYTHON","python3")}"}}\n'
    )

    if not cfg.exists():
        cfg.write_text(block, encoding="utf-8")
        return cfg

    body = cfg.read_text(encoding="utf-8")
    header = f"[mcp_servers.{server_name}]"
    if header in body:
        # 매우 단순한 치환(정교한 TOML 파서는 생략)
        pre, _, _rest = body.partition(header)
        # 블록 끝 추정: 다음 [ 로 시작하는 섹션 전까지
        post = body[len(pre):]
        next_idx = post.find("\n[")
        if next_idx != -1:
            post = post[next_idx:]  # 다음 섹션부터
            body = pre + block + post
        else:
            body = pre + block
    else:
        if not body.endswith("\n"): body += "\n"
        body += block
    cfg.write_text(body, encoding="utf-8")
    return cfg
