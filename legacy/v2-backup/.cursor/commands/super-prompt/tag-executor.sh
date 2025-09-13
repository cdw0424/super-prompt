#!/usr/bin/env bash
set -euo pipefail
# New tag-executor.sh that uses .super-prompt/utils structure
if command -v super-prompt >/dev/null 2>&1; then
  exec super-prompt optimize "$@"
else
  exec npx @cdw0424/super-prompt optimize "$@"
fi