#!/usr/bin/env zsh
set -euo pipefail
root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
missing=0

# Validate required markers
grep -q "Auto Model Router" "$root/AGENTS.md" || { echo "AGENTS.md missing AMR marker"; missing=1; }
grep -q "medium ↔ high" "$root/AGENTS.md" || { echo "AGENTS.md missing medium↔high"; missing=1; }
grep -q "router: switch to high" "$root/prompts/codex_amr_bootstrap_prompt_en.txt" || { echo "Bootstrap prompt missing router switch log"; missing=1; }

if [ "$missing" -ne 0 ]; then
  echo "--------router-check: FAIL"
  exit 1
fi
echo "--------router-check: OK"
