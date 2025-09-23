# packages/core-py/super_prompt/core/mcp_setup.py
"""
MCP 서버 초기화 및 설정 관련 기능
"""

import os
import sys
import inspect
from typing import Dict, Any, Optional, List


def _detect_mcp_version():
    """Detect MCP SDK version and capabilities with enhanced precision"""
    try:
        import mcp

        version = getattr(mcp, "__version__", "unknown")

        # Enhanced version detection logic
        if hasattr(mcp, "__version__") and mcp.__version__:
            version = mcp.__version__
            # Parse version string for more precise detection
            try:
                from packaging import version as pkg_version

                parsed_version = pkg_version.parse(version)
                if parsed_version >= pkg_version.parse("0.4.0"):
                    return f"{version} (0.4+)", "fastmcp"
                elif parsed_version >= pkg_version.parse("0.3.0"):
                    return f"{version} (0.3+)", "server"
                else:
                    return f"{version} (legacy)", "legacy"
            except ImportError:
                # packaging not available, use string comparison
                if version.startswith(("0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.")):
                    return f"{version} (0.4+)", "fastmcp"
                elif version.startswith("0.3"):
                    return f"{version} (0.3+)", "server"

        # Fallback to structural detection
        if hasattr(mcp, "server"):
            if hasattr(mcp.server, "FastMCP"):
                return "0.4+ (detected)", "fastmcp"
            elif hasattr(mcp.server, "fastmcp"):
                return "0.4+ (detected)", "fastmcp"
            elif hasattr(mcp.server, "Server"):
                return "0.3+ (detected)", "server"

        return version, "unknown"
    except Exception as e:
        return None, None


def _import_mcp_components():
    """Import MCP components with version compatibility"""
    mcp_version, mcp_type = _detect_mcp_version()

    if not mcp_version:
        raise ImportError("MCP SDK not available")

    # Try different import patterns for maximum compatibility
    import_attempts = [
        # MCP 0.4+ with FastMCP
        ("mcp.server.fastmcp", "FastMCP"),
        ("mcp.server", "FastMCP"),
        # MCP 0.3+ with Server
        ("mcp.server", "Server"),
        # Legacy patterns
        ("mcp", "FastMCP"),
    ]

    FastMCP = None
    for module_path, class_name in import_attempts:
        try:
            module = __import__(module_path, fromlist=[class_name])
            FastMCP = getattr(module, class_name, None)
            if FastMCP:
                break
        except (ImportError, AttributeError):
            continue

    if not FastMCP:
        raise ImportError(f"No compatible MCP FastMCP/Server class found in version {mcp_version}")

    # Try to import TextContent with comprehensive patterns
    text_content_attempts = [
        # Modern MCP patterns
        "mcp.types.TextContent",
        "mcp.server.models.TextContent",
        "mcp.shared.models.TextContent",
        "mcp.server.fastmcp.TextContent",
        # Alternative patterns
        "mcp.server.TextContent",
        "mcp.TextContent",
        # Legacy patterns for older versions
        "mcp.protocol.TextContent",
        "mcp.core.TextContent",
    ]

    TextContent = None
    for tc_path in text_content_attempts:
        try:
            module_path, class_name = tc_path.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            TextContent = getattr(module, class_name, None)
            if TextContent:
                break
        except (ImportError, AttributeError, ValueError):
            continue

    # Fallback TextContent class
    if not TextContent:

        class TextContent:  # minimal stub for direct-call mode
            def __init__(self, type: str, text: str):
                self.type = type
                self.text = text

    return FastMCP, TextContent, mcp_version


def _initialize_mcp_server():
    """Initialize MCP server with version-aware configuration"""
    try:
        FastMCP, _, _MCP_VERSION = _import_mcp_components()
    except Exception:
        return None

    try:
        # Try different initialization patterns for maximum compatibility
        server_name = "super-prompt"

        # Check FastMCP signature and initialize accordingly
        fastmcp_sig = inspect.signature(FastMCP)

        # Common initialization patterns across MCP versions
        init_attempts = [
            # Standard pattern for most versions
            lambda: FastMCP(server_name),
            # Some versions might require additional parameters
            lambda: FastMCP(name=server_name),
            # Alternative parameter patterns
            lambda: FastMCP(server_name, instructions=""),
            lambda: FastMCP(server_name, {}),
            lambda: FastMCP({"name": server_name}),
            # Legacy patterns for older versions
            lambda: FastMCP(server_name, None),
            lambda: FastMCP(server_name, {}, None),
        ]

        mcp_instance = None
        for init_func in init_attempts:
            try:
                mcp_instance = init_func()
                break
            except (TypeError, ValueError) as e:
                continue

        if mcp_instance is None:
            raise RuntimeError(f"Failed to initialize FastMCP with version {_MCP_VERSION}")

        return mcp_instance

    except Exception as e:
        return None


class MCPAuthorization:
    """MCP Authorization Framework for tool access control"""

    PERMISSION_LEVELS = {
        "read": 1,  # 읽기 전용 도구들
        "write": 2,  # 설정 변경 도구들
        "admin": 3,  # 시스템 관리 도구들
    }

    TOOL_PERMISSIONS = {
        # Read-only tools
        "version": "read",
        "list_commands": "read",
        "list_personas": "read",
        "mode_get": "read",
        "architect": "read",
        "frontend": "read",
        "backend": "read",
        "security": "read",
        "performance": "read",
        "analyzer": "read",
        "qa": "read",
        "refactorer": "read",
        "devops": "read",
        "mentor": "read",
        "scribe": "read",
        "dev": "read",
        "grok": "read",
        "db-expert": "read",
        "optimize": "read",
        "review": "read",
        "specify": "read",
        "plan": "read",
        "tasks": "read",
        "implement": "read",
        "seq": "read",
        "seq-ultra": "read",
        "high": "read",
        # Write tools (configuration changes)
        "mode_set": "write",
        "grok_mode_on": "write",
        "gpt_mode_on": "write",
        "grok_mode_off": "write",
        "gpt_mode_off": "write",
        # Admin tools (system modifications)
        "init": "admin",
        "refresh": "admin",
    }

    @classmethod
    def check_permission(cls, tool_name: str, user_level: str = "read") -> bool:
        """Check if user has permission to access a tool"""
        required_level = cls.TOOL_PERMISSIONS.get(tool_name, "read")
        user_perm_level = cls.PERMISSION_LEVELS.get(user_level, 1)
        required_perm_level = cls.PERMISSION_LEVELS.get(required_level, 1)

        return user_perm_level >= required_perm_level

    @classmethod
    def get_user_permission_level(cls) -> str:
        """Get current user's permission level from environment"""
        # Check for explicit permission level
        explicit_level = os.environ.get("SUPER_PROMPT_PERMISSION_LEVEL", "").lower()
        if explicit_level in cls.PERMISSION_LEVELS:
            return explicit_level

        flag = os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower()
        if flag in ("0", "false", "no"):
            return "read"

        return "admin"

    @classmethod
    def require_permission(cls, tool_name: str) -> None:
        """Require specific permission for tool access, raises exception if not authorized"""
        user_level = cls.get_user_permission_level()
        if not cls.check_permission(tool_name, user_level):
            required_level = cls.TOOL_PERMISSIONS.get(tool_name, "read")
            raise PermissionError(
                f"MCP: Insufficient permissions. Tool '{tool_name}' requires '{required_level}' level, "
                f"but user has '{user_level}' level. "
                f"Set SUPER_PROMPT_PERMISSION_LEVEL={required_level} to grant access."
            )
