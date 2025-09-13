#!/usr/bin/env bash
set -euo pipefail

# Join all args as a single input string
INPUT="$*"

# Known persona keys (must match enhanced_personas.yaml)
PERSONAS=(architect security performance backend frontend analyzer qa mentor refactorer devops scribe dev tr doc-master high)

# Try to detect a persona tag like /architect
DETECTED=""
for P in "${PERSONAS[@]}"; do
  if [[ "$INPUT" == *"/$P"* ]]; then
    DETECTED="$P"
    break
  fi
done

DELEGATE_FLAG=""
if [[ "$INPUT" == *"/delegate"* ]]; then
  INPUT="${INPUT//\/delegate/}"
  DELEGATE_FLAG="--delegate-reasoning"
fi

if [[ -n "$DETECTED" ]]; then
  # Clean the input by removing the persona tag
  CLEANED_INPUT="${INPUT//\/$DETECTED/}"

  # Resolve processor path
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  PROJECT_ROOT="${SCRIPT_DIR%/.cursor/commands/super-prompt}"
  PROCESSOR_PATH="$PROJECT_ROOT/.super-prompt/utils/cursor-processors/enhanced_persona_processor.py"

  if command -v python3 >/dev/null 2>&1 && [[ -f "$PROCESSOR_PATH" ]]; then
    exec python3 "$PROCESSOR_PATH" --persona "$DETECTED" --user-input "$CLEANED_INPUT" $DELEGATE_FLAG
  fi
fi

# Fallback to default optimize if no persona detected or processor unavailable
if command -v super-prompt >/dev/null 2>&1; then
  exec super-prompt optimize "$@"
else
  exec npx @cdw0424/super-prompt optimize "$@"
fi
