#!/usr/bin/env bash
set -euo pipefail

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
