#!/usr/bin/env python3
"""
Minimal MCP stdio entrypoint (uv/video style)

Runs the Super Prompt MCP server using stdio transport so MCP clients
like Cursor/VS Code can connect the same way as in the reference video.
"""

from super_prompt.mcp_app import mcp


def main() -> None:
    # stdio is the safest/fastest local transport
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()


