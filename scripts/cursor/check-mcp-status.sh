#!/bin/bash
# Cursor CLI script for checking MCP server connectivity
# Usage: ./scripts/cursor/check-mcp-status.sh

set -e

echo "🔌 Checking MCP server connectivity..."
echo ""

# Check if cursor-agent is available
if ! command -v cursor-agent &> /dev/null; then
    echo "❌ cursor-agent not found. Install with:"
    echo "   curl https://cursor.com/install -fsS | bash"
    exit 1
fi

# Check MCP status
echo "Checking global MCP configuration..."
cursor-agent mcp

echo ""
echo "Checking project-specific MCP servers..."
if [ -f "mcp-config.json" ]; then
    echo "Found project MCP config: mcp-config.json"
fi

if [ -f "~/.cursor/mcp.json" ]; then
    echo "Found global MCP config: ~/.cursor/mcp.json"
fi

echo ""
echo "✅ MCP status check complete."
