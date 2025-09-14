#!/usr/bin/env zsh
set -euo pipefail

# Super Prompt Router Check
# Validates AMR integration and SDD compliance

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
AGENTS_PATH=""
for p in "$root/.codex/agents.md" "$root/.codex/AGENTS.md" "$root/AGENTS.md"; do
  if [ -f "$p" ]; then AGENTS_PATH="$p"; break; fi
done

if [ -z "$AGENTS_PATH" ]; then
  echo "--------router-check: FAIL (no agents/AGENTS.md found)"
  exit 1
fi

missing=0
grep -q "Auto Model Router" "$AGENTS_PATH" || { echo "AGENTS.md missing AMR marker"; missing=1; }
grep -q "medium ↔ high" "$AGENTS_PATH" || { echo "AGENTS.md missing medium↔high"; missing=1; }
grep -q "SDD" "$AGENTS_PATH" || { echo "AGENTS.md missing SDD reference"; missing=1; }

if [ "$missing" -ne 0 ]; then
  echo "--------router-check: FAIL"
  exit 1
fi

echo "--------router-check: OK"
