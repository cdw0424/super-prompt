#!/usr/bin/env bash
set -euo pipefail

# TAG COMMAND PRIORITY SYSTEM
# ============================
# CRITICAL: Tag commands execute FIRST, regardless of prompt position
# Tag commands are TOOLS that upgrade persona/prompt WITHOUT affecting user context
# Tag command activation is GUARANTEED at highest priority

# Prefer project-local Python CLI to work without global super-prompt
if [ -f ".super-prompt/cli.py" ]; then
  if [ -x ".super-prompt/venv/bin/python" ]; then
    PY=".super-prompt/venv/bin/python"
  else
    PY="python3"
  fi
  exec "$PY" ".super-prompt/cli.py" optimize "$@"
fi

# Fallbacks: global or npx
if command -v super-prompt >/dev/null 2>&1; then
  exec super-prompt optimize "$@"
else
  exec npx @cdw0424/super-prompt optimize "$@"
fi
