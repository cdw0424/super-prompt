#!/usr/bin/env bash
set -euo pipefail

echo "-------- mode-smoke: start"

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT_DIR"

MODE_FILE=".super-prompt/mode.json"

show_mode() {
  if [ -f "$MODE_FILE" ]; then
    mode=$(node -e "console.log(require('fs').existsSync('$MODE_FILE') ? JSON.parse(require('fs').readFileSync('$MODE_FILE','utf8')).llm_mode : 'missing')")
    echo "-------- current mode: ${mode}"
  else
    echo "-------- current mode: (none)"
  fi
}

echo "-------- step: set mode → gpt"
node src/mode/set.js gpt >/dev/null
show_mode

echo "-------- step: set mode → grok"
node src/mode/set.js grok >/dev/null
show_mode

echo "-------- mode-smoke: OK"

