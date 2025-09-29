#!/bin/bash
# Cursor CLI script for refactoring duplicate code
# Usage: ./scripts/cursor/refactor-duplicates.sh

set -e

echo "🔧 Refactoring duplicated helpers into a single utility with tests..."
echo ""

# Check if cursor-agent is available
if ! command -v cursor-agent &> /dev/null; then
    echo "❌ cursor-agent not found. Install with:"
    echo "   curl https://cursor.com/install -fsS | bash"
    exit 1
fi

# Run the refactoring
cursor-agent "Refactor duplicated helpers into a single utility with tests."

echo ""
echo "✅ Refactoring complete."
