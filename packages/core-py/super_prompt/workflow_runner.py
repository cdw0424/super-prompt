#!/usr/bin/env python3
"""
Workflow Runner - Direct execution of prompt-based workflows
This module allows direct execution of MCP server workflows without MCP protocol
"""

import sys
import os
import traceback

# Add the core-py package to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set environment to bypass MCP restrictions
os.environ['MCP_INLINE_MODE'] = '1'

def run_workflow(persona_name: str, query: str, mode: str = "gpt") -> str:
    """
    Direct execution of prompt-based workflow or codex CLI with sandbox
    """
    # Silent workflow execution start for clean MCP operation

    # Note: high persona now executes directly from high.md (no longer uses workflow_runner)

    try:
        # Import required modules for other personas
        from super_prompt.mcp_server import run_prompt_based_workflow as original_workflow
        # Silent mcp_server import success for clean MCP operation

        from super_prompt.mode_store import get_mode
        # Silent utils import success for clean MCP operation

    except Exception as import_error:
        # Silent import error for clean MCP operation
        pass
        return f"IMPORT ERROR: {str(import_error)}"

    try:

        # Set inline mode environment variable to bypass MCP restrictions
        os.environ['MCP_SERVER_MODE'] = '1'  # This should allow execution

        # Get current mode
        current_mode = get_mode() if mode == "auto" else mode

        # Silent execution info for clean MCP operation

        # Execute the workflow
        result = original_workflow(persona_name, query, current_mode)

        # Silent completion info for clean MCP operation

        return result if result else "No result returned from workflow"

    except Exception as e:
        error_msg = f"Error executing {persona_name} workflow: {str(e)}"
        # Silent error output for clean MCP operation
        return f"ERROR: {error_msg}"


# Removed: run_codex_cli_high() - high persona now executes directly from high.md

if __name__ == "__main__":
    # Silent startup info for clean MCP operation

    if len(sys.argv) < 3:
        # Silent usage error for clean MCP operation
        sys.exit(1)

    persona = sys.argv[1]
    query = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else "auto"

    # Silent workflow call info for clean MCP operation

    result = run_workflow(persona, query, mode)
    # Silent final result output for clean MCP operation
    # Removed stdout print to preserve MCP protocol
