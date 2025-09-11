#!/usr/bin/env zsh
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "Usage: $0 <transcript.txt>" >&2
  exit 2
fi
f="$1"
if [ ! -f "$f" ]; then
  echo "File not found: $f" >&2
  exit 2
fi

rc=0

# 1) Sections present
grep -q '^\[INTENT\]' "$f" || { echo '--------qa: Missing [INTENT]'; rc=1; }
grep -Eq '^\[PLAN\]|^\[EXECUTE\]' "$f" || { echo '--------qa: Missing [PLAN] or [EXECUTE]'; rc=1; }

# 2) Log prefix discipline
if grep -qE '^(router:|run:)' "$f"; then
  echo '--------qa: Log prefix violation (use --------)'; rc=1
fi

# 3) Router switch consistency (best-effort)
if grep -q '/model gpt-5 high' "$f" && ! grep -q '/model gpt-5 medium' "$f"; then
  echo '--------qa: High switch without return to medium'; rc=1
fi

if [ "$rc" -eq 0 ]; then
  echo '--------qa: OK'
else
  echo '--------qa: FAIL'
fi
exit "$rc"
