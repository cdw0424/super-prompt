#!/usr/bin/env python3.12

import sys
import os
from pathlib import Path

# Add the core-py package to Python path
sys.path.insert(0, str(Path(__file__).parent / 'packages' / 'core-py'))

# Enable verbose logging
os.environ['SUPER_PROMPT_VERBOSE'] = '1'

print("Testing MCP server startup...")
print(f"Python path: {sys.path[0]}")

try:
    # Import MCP components
    from super_prompt.mcp.version_detection import import_mcp_components
    print("Successfully imported version_detection")

    # Try to import MCP components
    FastMCP, TextContent, version = import_mcp_components()
    print(f"Success! FastMCP: {FastMCP}")
    print(f"Version: {version}")
    print(f"TextContent: {TextContent}")

    # Try to create a simple MCP server
    if FastMCP:
        print("Creating MCP server instance...")
        mcp = FastMCP("test-server")
        print("MCP server created successfully!")
        print(f"MCP instance: {mcp}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
