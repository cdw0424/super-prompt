"""
MCP Authorization Framework for tool access control
"""

import os
from typing import Dict


class MCPAuthorization:
    """MCP Authorization Framework for tool access control"""

    PERMISSION_LEVELS = {
        "read": 1,  # Read-only tools
        "write": 2,  # Configuration change tools
        "admin": 3,  # System management tools
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

        # Check for admin access
        if os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower() in ("1", "true", "yes"):
            return "admin"

        # Default to read-only
        return "read"

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
