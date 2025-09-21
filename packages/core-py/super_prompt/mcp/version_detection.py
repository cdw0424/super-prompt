"""
MCP SDK version detection and component imports
"""

import sys
import os
from typing import Tuple, Optional, Any


def detect_mcp_version() -> Tuple[Optional[str], Optional[str]]:
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
        # Silent version detection failure (no logging)
        return None, None


def import_mcp_components():
    """Import MCP components with version compatibility"""
    mcp_version, mcp_type = detect_mcp_version()

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


def create_fallback_mcp():
    """Create fallback MCP stub when SDK is unavailable"""
    
    class TextContent:  # minimal stub for direct-call mode
        def __init__(self, type: str, text: str):
            self.type = type
            self.text = text

    class _StubMCP:
        def tool(self, *_args, **_kwargs):
            def _decorator(fn):
                return fn
            return _decorator

        def prompt(self, *_args, **_kwargs):
            def _decorator(fn):
                return fn
            return _decorator

        def run(self):
            raise RuntimeError("MCP SDK not available; cannot start MCP server")

    return _StubMCP(), TextContent
