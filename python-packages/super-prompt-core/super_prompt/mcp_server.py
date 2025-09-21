# packages/core-py/super_prompt/mcp_server.py
# ⚠️ DEPRECATED: This module has been modularized
#
# The MCP server functionality has been split into:
# - mcp/: MCP SDK integration and version detection
# - utils/: Span management, progress display, authorization  
# - pipeline/: Pipeline configuration and execution logic
# - tools/: Tool registration and metadata management
# - personas/tools/: Individual persona tool implementations
# - codex/: Codex integration and assistance
# - mcp_server_new.py: Clean main server module
#
# This file is kept for backward compatibility during transition.
# New code should use the modularized structure instead.
#
# SECURITY: MCP-only access - Direct CLI calls are blocked
# pip dep: mcp >= 0.4.0

"""
DEPRECATED: Use mcp_server_new.py instead

This file now imports from the modularized components for backward compatibility.
All new development should use the modular structure.
"""

# Import everything from the new modular server
from .mcp_server_new import *

# Backward compatibility imports
from .utils.span_manager import span_manager
from .utils.progress import progress
from .utils.authorization import MCPAuthorization
from .tools.registry import register_tool, REGISTERED_TOOL_ANNOTATIONS
from .pipeline.executor import run_persona_pipeline, get_pipeline_config, PIPELINE_CONFIGS
from .codex.integration import call_codex_assistance, should_use_codex_assistance

import warnings
warnings.warn(
    "mcp_server.py is deprecated. Use mcp_server_new.py and modular imports instead.",
    DeprecationWarning,
    stacklevel=2
)
