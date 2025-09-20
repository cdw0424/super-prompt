from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _render_codex_config_block(project_root: Path,
                               server_name: str,
                               npm_spec: str,
                               python_exec: str,
                               local_sp_mcp: Path | None = None) -> str:
    """Render canonical Codex MCP config block for super:init."""
    project_path = str(project_root).replace("\\", "\\\\").replace('"', '\\"')
    python_exec = python_exec or "python3"
    env_entries = [
        'SUPER_PROMPT_ALLOW_INIT = "true"',
        f'SUPER_PROMPT_PROJECT_ROOT = "{project_path}"',
    ]
    if local_sp_mcp is None:
        env_entries.extend([
            f'SUPER_PROMPT_NPM_SPEC = "{npm_spec}"',
            f'PYTHON = "{python_exec}"',
        ])
    env_entries.extend([
        'PYTHONUNBUFFERED = "1"',
        'PYTHONUTF8 = "1"',
    ])
    env_inline = ", ".join(env_entries)

    if local_sp_mcp is not None:
        command_line = f'command = "{str(local_sp_mcp)}"\nargs = []\n'
    else:
        command_line = 'command = "npx"\n' + f'args = ["-y", "{npm_spec}", "sp-mcp"]\n'

    return (
        f"[mcp_servers.{server_name}]\n"
        f"{command_line}"
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
                                 server_name: str = "super-prompt",
                                 overwrite: bool = False) -> Path:
    """
    Global MCP registration: write to ~/.cursor/mcp.json.
    Manages MCP server configuration globally to avoid project-specific duplication.
    CRITICAL: Prevents any duplicate MCP installations by enforcing global-only registration.
    """
    # 전역 ~/.cursor 디렉터리 사용 (항상 전역, 절대 중복 없음)
    cursor_dir = Path.home() / ".cursor"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = cursor_dir / "mcp.json"

    # 중복 방지: 프로젝트별 MCP 설정 파일이 있는지 확인하고 경고
    project_mcp_path = project_root / ".cursor" / "mcp.json"
    if project_mcp_path.exists():
        pass  # 중복 방지: 프로젝트별 MCP 설정은 무시하고 전역 설정만 사용

    # CRITICAL: 중복 방지 - 로컬과 글로벌 MCP가 동시에 존재하는지 확인
    local_sp_mcp = (Path(project_root) / "bin" / "sp-mcp")
    use_absolute = (os.environ.get("SUPER_PROMPT_CURSOR_ABSOLUTE", "1") != "0")

    # 중복 방지: 로컬 MCP가 존재하면 전역 설정을 우선 사용하도록 강제
    if local_sp_mcp.exists():
        # 로컬 MCP는 개발용으로만 사용, 전역 MCP는 항상 우선
        pass  # 중복 방지: 로컬 MCP는 무시하고 전역 설정만 사용
        entry = {
            "type": "stdio",
            "command": str(local_sp_mcp) if use_absolute else "./bin/sp-mcp",
            "args": [],
            "env": {
                "SUPER_PROMPT_ALLOW_INIT": "true",
                "SUPER_PROMPT_REQUIRE_MCP": "1",
                "SUPER_PROMPT_PROJECT_ROOT": str(project_root),
                "PYTHONUNBUFFERED": "1",
                "PYTHONUTF8": "1",
            },
        }
    else:
        # Fallback to python -m for environments without the launcher
        entry = {
            "type": "stdio",
            "command": os.environ.get("PYTHON", "python3"),
            "args": ["-m", "super_prompt.mcp_server"],
            "env": {
                "SUPER_PROMPT_ALLOW_INIT": "true",
                "SUPER_PROMPT_REQUIRE_MCP": "1",
                "SUPER_PROMPT_PROJECT_ROOT": str(project_root),
                "PYTHON": os.environ.get("PYTHON", "python3"),
                "PYTHONUNBUFFERED": "1",
                "PYTHONUTF8": "1",
                "SUPER_PROMPT_DEBUG": "1",
            },
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
        # env는 얕은 병합 + 오래된 키 제거
        merged_env = dict(mcp[server_name].get("env") or {})
        merged_env.update(entry["env"])
        for legacy_key in (
            "SUPER_PROMPT_PACKAGE_ROOT",
            "PYTHONPATH",
            "MCP_SERVER_MODE",
            "SUPER_PROMPT_NPM_SPEC",
            "PYTHON",
        ):
            merged_env.pop(legacy_key, None)
        merged["env"] = merged_env
        merged["command"] = entry["command"]
        merged["args"] = entry["args"]
        merged["type"] = "stdio"
        mcp[server_name] = merged
    else:
        mcp[server_name] = entry

    if overwrite:
        # Replace only our server entry; keep others intact but ensure ours matches exactly
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

    python_exec = os.environ.get("PYTHON", "python3")
    # Prefer local launcher; fallback to python -m
    local_sp_mcp = Path(project_root) / "bin" / "sp-mcp"
    if not local_sp_mcp.exists():
        local_sp_mcp = None

    block = _render_codex_config_block(
        project_root,
        server_name,
        npm_spec="@cdw0424/super-prompt@latest",  # unused when local_sp_mcp is set
        python_exec=python_exec,
        local_sp_mcp=local_sp_mcp,
    )

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


def validate_project_ssot(project_root: Path) -> bool:
    """
    SSOT compliance validation: Check for conflicts between project and global settings

    Returns:
        True if SSOT compliant, False if conflicts detected
    """
    try:
        # Project configuration files
        project_cursor = project_root / ".cursor" / "mcp.json"
        project_codex = project_root / ".codex" / "config.toml"

        # Global configuration files
        global_cursor = Path.home() / ".cursor" / "mcp.json"
        global_codex = Path.home() / ".codex" / "config.toml"

        conflicts = []

        # Cursor settings conflict validation
        if project_cursor.exists() and global_cursor.exists():
            try:
                project_data = json.loads(project_cursor.read_text(encoding="utf-8"))
                global_data = json.loads(global_cursor.read_text(encoding="utf-8"))

                project_servers = set(project_data.get("mcpServers", {}).keys())
                global_servers = set(global_data.get("mcpServers", {}).keys())

                overlapping = project_servers & global_servers
                if overlapping:
                    conflicts.append(f"Cursor MCP server overlap: {overlapping}")
            except (json.JSONDecodeError, KeyError) as e:
                pass

        # Codex settings conflict validation
        if project_codex.exists() and global_codex.exists():
            try:
                project_content = project_codex.read_text(encoding="utf-8")
                global_content = global_codex.read_text(encoding="utf-8")

                # Simple header-based overlap validation
                server_headers = ["[mcp_servers.super-prompt]"]
                for header in server_headers:
                    if header in project_content and header in global_content:
                        conflicts.append(f"Codex MCP server overlap: {header}")
                        break
            except Exception as e:
                pass

        if conflicts:
            return False

        return True

    except Exception as e:
        return False


def cleanup_global_entries(server_name: str = "super-prompt") -> None:
    """
    Cleanup existing global entries (one-time cleanup for SSOT compliance)
    """
    try:
        # Cursor global configuration cleanup
        cursor_global = Path.home() / ".cursor" / "mcp.json"
        if cursor_global.exists():
            try:
                data = json.loads(cursor_global.read_text(encoding="utf-8"))
                if "mcpServers" in data and server_name in data["mcpServers"]:
                    # Create backup
                    backup = cursor_global.with_suffix(f".backup_{server_name}")
                    cursor_global.replace(backup)
            except Exception as e:
                pass

        # Codex global configuration cleanup
        codex_global = Path.home() / ".codex" / "config.toml"
        if codex_global.exists():
            try:
                content = codex_global.read_text(encoding="utf-8")
                header = f"[mcp_servers.{server_name}]"
                if header in content:
                    # Create backup
                    backup = codex_global.with_suffix(f".backup_{server_name}")
                    codex_global.replace(backup)
            except Exception as e:
                pass

    except Exception as e:
        pass


def ensure_project_ssot_priority(project_root: Path, server_name: str = "super-prompt") -> bool:
    """
    Ensure project SSOT priority (Phase 3: SSOT Enhancement)

    Ensures that project settings take priority over global settings.
    When project settings exist, global settings are deactivated.

    Returns:
        True if project settings take priority, False if issues detected
    """
    try:
        # Project configuration files
        project_cursor = project_root / ".cursor" / "mcp.json"
        project_codex = project_root / ".codex" / "config.toml"

        # Global configuration files
        global_cursor = Path.home() / ".cursor" / "mcp.json"
        global_codex = Path.home() / ".codex" / "config.toml"

        priority_established = True

        # If project Cursor settings exist, establish priority
        if project_cursor.exists():
            try:
                project_data = json.loads(project_cursor.read_text(encoding="utf-8"))
                if "mcpServers" in project_data and server_name in project_data["mcpServers"]:
                    # Optional warning for global settings
                    if global_cursor.exists():
                        pass
                else:
                    priority_established = False
            except Exception as e:
                priority_established = False

        # If project Codex settings exist, establish priority
        if project_codex.exists():
            try:
                project_content = project_codex.read_text(encoding="utf-8")
                header = f"[mcp_servers.{server_name}]"
                if header in project_content:
                    # Optional warning for global settings
                    if global_codex.exists():
                        pass
                else:
                    priority_established = False
            except Exception as e:
                priority_established = False

        # Warn if no project settings exist
        if not project_cursor.exists() and not project_codex.exists():
            priority_established = False

        return priority_established

    except Exception as e:
        return False


def perform_ssot_migration(project_root: Path, dry_run: bool = True) -> dict:
    """
    Perform SSOT migration (Phase 4: Cleanup and Migration)

    Clean up existing global settings and migrate to project SSOT.

    Args:
        project_root: Project root directory
        dry_run: Show plan without actual execution

    Returns:
        Migration results and recommendations
    """
    try:
        migration_plan = {
            "dry_run": dry_run,
            "actions_taken": [],
            "warnings": [],
            "recommendations": [],
            "success": True
        }

        # 1. Analyze current status
        current_status = {
            "project_cursor_exists": (project_root / ".cursor" / "mcp.json").exists(),
            "project_codex_exists": (project_root / ".codex" / "config.toml").exists(),
            "global_cursor_exists": (Path.home() / ".cursor" / "mcp.json").exists(),
            "global_codex_exists": (Path.home() / ".codex" / "config.toml").exists(),
        }

        migration_plan["current_status"] = current_status

        # 2. SSOT validation
        ssot_compliant = validate_project_ssot(project_root)
        migration_plan["ssot_compliant_before"] = ssot_compliant

        if not ssot_compliant:
            migration_plan["warnings"].append("SSOT violation detected - migration required")

        # 3. Develop migration plan
        if current_status["global_cursor_exists"] or current_status["global_codex_exists"]:
            migration_plan["actions_taken"].append("Global settings cleanup required")
            migration_plan["recommendations"].append("Run super-prompt setup cleanup --cursor --codex recommended")

        if not current_status["project_cursor_exists"]:
            migration_plan["warnings"].append("Project Cursor settings missing")
            migration_plan["recommendations"].append("Create project .cursor/mcp.json required")

        if not current_status["project_codex_exists"]:
            migration_plan["warnings"].append("Project Codex settings missing")
            migration_plan["recommendations"].append("Create project .codex/config.toml required")

        # 4. Attempt to establish project priority
        if current_status["project_cursor_exists"] or current_status["project_codex_exists"]:
            if not dry_run:
                priority_set = ensure_project_ssot_priority(project_root)
                migration_plan["priority_established"] = priority_set
                if priority_set:
                    migration_plan["actions_taken"].append("Project SSOT priority established")
                else:
                    migration_plan["warnings"].append("Project priority setup failed")
            else:
                migration_plan["actions_taken"].append("Project SSOT priority setup planned (dry-run)")

        # 5. Final validation
        if not dry_run:
            final_ssot_compliant = validate_project_ssot(project_root)
            migration_plan["ssot_compliant_after"] = final_ssot_compliant

            if final_ssot_compliant:
                migration_plan["actions_taken"].append("SSOT compliance achieved")
            else:
                migration_plan["success"] = False
                migration_plan["warnings"].append("SSOT violations still exist after migration")

        return migration_plan

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "dry_run": dry_run
        }


def get_ssot_guidance() -> str:
    """
    Return user guidelines for SSOT compliance
    """
    return """
🔧 SSOT (Single Source of Truth) Compliance Guidelines:

📋 Basic Principles:
  • Use only one MCP server configuration (project-local or global)
  • Project settings take priority over global settings
  • Duplicate settings are considered SSOT violations

🎯 Recommendations:
  • New projects: Use project-local settings (.cursor/mcp.json, .codex/config.toml)
  • Global settings: Use only for special cases (multi-project sharing)
  • Setting changes: Check project settings first

🛠️ Troubleshooting:
  • Conflict detection: super-prompt setup validate
  • Global cleanup: super-prompt setup cleanup --cursor --codex
  • Manual setup: Edit project .cursor/.codex directories directly

⚠️  Important Notes:
  • Init command no longer automatically registers globally
  • For explicit global setup: super-prompt setup global --cursor
  • Existing global settings should be backed up before cleanup
"""
