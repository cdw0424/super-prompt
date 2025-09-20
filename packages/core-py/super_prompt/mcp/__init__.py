"""
MCP (Model Context Protocol) integration module
"""

from .version_detection import detect_mcp_version, import_mcp_components, create_fallback_mcp

__all__ = [
    "detect_mcp_version",
    "import_mcp_components", 
    "create_fallback_mcp"
]
