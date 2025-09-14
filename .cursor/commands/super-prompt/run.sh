#!/bin/bash
# Super Prompt Cursor Integration - Unified CLI Router
# Routes all Super Prompt commands through the unified CLI

# Set cursor mode for context detection
export CURSOR_MODE=1

# Execute the unified CLI with all arguments
python3 "$(dirname "$0")/../../.super-prompt/unified_cli.py" "$@"