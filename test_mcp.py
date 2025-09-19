#!/usr/bin/env python3
import sys
import os

# Set up paths
sys.path.insert(0, '/Users/choi-dong-won/Desktop/devs/super-promt/packages/core-py')
os.environ['MCP_SERVER_MODE'] = '1'

# Import and check mode first
try:
    print("-------- MCP: Test script loaded successfully", file=sys.stderr, flush=True)

    # Check mode before importing MCP server
    from super_prompt.mode_store import get_mode
    current_mode = get_mode()
    print(f"-------- mode: resolved to {current_mode}", file=sys.stderr, flush=True)

    if current_mode == 'grok':
        print("-------- SUCCESS: Grok mode detected correctly!", file=sys.stderr, flush=True)
    else:
        print(f"-------- WARNING: Expected grok mode but got {current_mode}", file=sys.stderr, flush=True)

    # Now try to import MCP server (but don't start it due to asyncio issues)
    print("-------- MCP: Importing MCP server module...", file=sys.stderr, flush=True)
    import super_prompt.mcp_server as mcp_server
    print("-------- MCP: Module imported successfully", file=sys.stderr, flush=True)

except Exception as e:
    print(f"-------- ERROR: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc()
