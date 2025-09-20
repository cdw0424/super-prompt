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
    print(f"-------- workflow_runner: About to execute {persona_name}...", file=sys.stderr)

    # Note: high persona now executes directly from high.md (no longer uses workflow_runner)

    try:
        # Import required modules for other personas
        from super_prompt.mcp_server import run_prompt_based_workflow as original_workflow
        print(f"-------- workflow_runner: mcp_server imported successfully", file=sys.stderr)

        from super_prompt.mode_store import get_mode
        print(f"-------- workflow_runner: utils imported successfully", file=sys.stderr)

    except Exception as import_error:
        print(f"-------- workflow_runner: Import error: {str(import_error)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return f"IMPORT ERROR: {str(import_error)}"

    try:

        # Set inline mode environment variable to bypass MCP restrictions
        os.environ['MCP_SERVER_MODE'] = '1'  # This should allow execution

        # Get current mode
        current_mode = get_mode() if mode == "auto" else mode

        print(f"-------- workflow_runner: Executing {persona_name} with mode {current_mode}", file=sys.stderr)

        # Execute the workflow
        result = original_workflow(persona_name, query, current_mode)

        print(f"-------- workflow_runner: Workflow completed, result length: {len(result) if result else 0}", file=sys.stderr)

        return result if result else "No result returned from workflow"

    except Exception as e:
        error_msg = f"Error executing {persona_name} workflow: {str(e)}"
        print(error_msg, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return f"ERROR: {error_msg}"


# Removed: run_codex_cli_high() - high persona now executes directly from high.md

if __name__ == "__main__":
    print(f"-------- workflow_runner: Starting with args: {sys.argv}", file=sys.stderr)

    if len(sys.argv) < 3:
        print("Usage: python workflow_runner.py <persona> <query> [mode]", file=sys.stderr)
        sys.exit(1)

    persona = sys.argv[1]
    query = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else "auto"

    print(f"-------- workflow_runner: Calling run_workflow({persona}, {query}, {mode})", file=sys.stderr)

    result = run_workflow(persona, query, mode)
    print(f"-------- workflow_runner: Final result: {result[:100] if result else 'None'}", file=sys.stderr)
    print(result)
