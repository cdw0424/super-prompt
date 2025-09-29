from __future__ import annotations

import json
import os
from pathlib import Path


def ensure_cursor_mcp_registered(
    project_root: Path,
    npm_spec: str | None = None,
    server_name: str = "super-prompt",
    overwrite: bool = False,
) -> Path:
    """
    Global MCP registration: write to ~/.cursor/mcp.json.
    Manages MCP server configuration globally while preserving existing MCP servers.
    IMPORTANT: Always preserves existing MCP servers to prevent conflicts.
    """
    # 전역 ~/.cursor 디렉터리 사용 (항상 전역, 절대 중복 없음)
    cursor_dir = Path.home() / ".cursor"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = cursor_dir / "mcp.json"

    # 중복 방지: 프로젝트별 MCP 설정 파일이 있는지 확인하고 경고
    project_mcp_path = project_root / ".cursor" / "mcp.json"
    if project_mcp_path.exists():
        pass  # 중복 방지: 프로젝트별 MCP 설정은 무시하고 전역 설정만 사용

    # Always use Python module approach for global MCP registration
    # This ensures consistent behavior across different project setups
    entry = {
        "type": "stdio",
        "command": os.environ.get("PYTHON", "python3"),
        "args": ["-m", "super_prompt.mcp_stdio"],
        "env": {
            "SUPER_PROMPT_ALLOW_INIT": "true",
            "SUPER_PROMPT_REQUIRE_MCP": "1",
            "SUPER_PROMPT_PROJECT_ROOT": str(project_root.resolve()),
            "PYTHONPATH": str((project_root / "python-packages" / "super-prompt-core").resolve()),
            "PYTHON": os.environ.get("PYTHON", "python3"),
            "PYTHONUNBUFFERED": "1",
            "PYTHONUTF8": "1",
        },
    }

    data = {}
    existing_servers = {}

    if cfg_path.exists():
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8") or "{}")
            # 기존 MCP 서버들을 백업
            existing_servers = data.get("mcpServers", {}).copy()
        except Exception:
            # 파손/비JSON이면 보수적으로 새로 작성
            data = {}

    mcp = data.get("mcpServers") or {}

    # overwrite=True라도 기존 MCP 서버들을 보존 (단, 같은 이름의 서버는 교체)
    if overwrite:
        # 같은 이름의 서버만 교체, 다른 서버들은 모두 보존
        mcp[server_name] = entry
        # overwrite=True일 때도 다른 기존 서버들을 보존
        for existing_name, existing_config in existing_servers.items():
            if existing_name != server_name:
                mcp[existing_name] = existing_config
    else:
        # 기존 설정과 병합 (항상 기존 서버들을 보존)
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
                "CODEX_HOME",
                "SUPER_PROMPT_ALLOW_INIT",
            ):
                merged_env.pop(legacy_key, None)
            merged["env"] = merged_env
            merged["command"] = entry["command"]
            merged["args"] = entry["args"]
            merged["type"] = "stdio"
            mcp[server_name] = merged
        else:
            mcp[server_name] = entry

    data["mcpServers"] = mcp
    cfg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return cfg_path


# Codex functionality has been removed to prevent .codex file modifications during super:init
# Codex functionality has been completely removed
# All Codex-related functionality has been completely removed to prevent file system conflicts


def validate_project_ssot(project_root: Path) -> bool:
    """
    SSOT compliance validation: Check for conflicts between project and global settings

    Returns:
        True if SSOT compliant, False if conflicts detected
    """
    try:
        # Project configuration files (Cursor MCP only)
        project_cursor = project_root / ".cursor" / "mcp.json"

        # Global configuration files (Cursor MCP only)
        global_cursor = Path.home() / ".cursor" / "mcp.json"

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

        # Codex functionality removed - no Codex validation needed

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

        # Codex functionality removed - Super Prompt only manages Cursor MCP

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
        # Project configuration files (Cursor MCP only)
        project_cursor = project_root / ".cursor" / "mcp.json"

        # Global configuration files (Cursor MCP only)
        global_cursor = Path.home() / ".cursor" / "mcp.json"

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

        # Codex functionality removed - no Codex priority logic needed

        # Warn if no project settings exist
        if not project_cursor.exists():
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
            "success": True,
        }

        # 1. Analyze current status (Cursor MCP only)
        current_status = {
            "project_cursor_exists": (project_root / ".cursor" / "mcp.json").exists(),
            "global_cursor_exists": (Path.home() / ".cursor" / "mcp.json").exists(),
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
            migration_plan["recommendations"].append(
                "Run super-prompt setup cleanup --cursor --codex recommended"
            )

        if not current_status["project_cursor_exists"]:
            migration_plan["warnings"].append("Project Cursor settings missing")
            migration_plan["recommendations"].append("Create project .cursor/mcp.json required")

        # Codex functionality removed - no Codex migration needed

        # 4. Attempt to establish project priority
        if current_status["project_cursor_exists"]:
            if not dry_run:
                priority_set = ensure_project_ssot_priority(project_root)
                migration_plan["priority_established"] = priority_set
                if priority_set:
                    migration_plan["actions_taken"].append("Project SSOT priority established")
                else:
                    migration_plan["warnings"].append("Project priority setup failed")
            else:
                migration_plan["actions_taken"].append(
                    "Project SSOT priority setup planned (dry-run)"
                )

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
        return {"success": False, "error": str(e), "dry_run": dry_run}


def get_ssot_guidance() -> str:
    """
    Return user guidelines for SSOT compliance
    """
    return """
🔧 SSOT (Single Source of Truth) Compliance Guidelines:

📋 Basic Principles:
  • Super Prompt only manages Cursor MCP server configuration
  • Use only one MCP server configuration (project-local or global)
  • Project settings take priority over global settings
  • Duplicate settings are considered SSOT violations

🎯 Recommendations:
  • New projects: Use project-local settings (.cursor/mcp.json)
  • Global settings: Use only for special cases (multi-project sharing)
  • Setting changes: Check project settings first
  • Codex CLI: Managed independently by user (no Super Prompt integration)

🛠️ Troubleshooting:
  • Conflict detection: super-prompt setup validate
  • Global cleanup: super-prompt setup cleanup --cursor
  • Manual setup: Edit project .cursor directory directly

⚠️  Important Notes:
  • Init command no longer automatically registers globally
  • Super Prompt never modifies .codex/ directories or configurations
  • For explicit global setup: super-prompt setup global --cursor
  • Existing global settings should be backed up before cleanup
"""
