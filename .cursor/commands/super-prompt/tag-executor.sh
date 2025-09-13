#!/usr/bin/env bash
set -euo pipefail

# Join all args as a single input string
INPUT="$*"

# Known persona keys (must match enhanced_personas.yaml)
PERSONAS=(architect security performance backend frontend analyzer qa mentor refactorer devops scribe dev tr doc-master high debate frontend-ultra seq seq-ultra docs-refector ultracompressed wave task implement plan review spec specify init-sp re-init-sp)

# Try to detect a persona tag like /architect
DETECTED=""
SPECIAL_COMMANDS=("init-sp" "re-init-sp")

# Check for special initialization commands first
for CMD in "${SPECIAL_COMMANDS[@]}"; do
  if [[ "$INPUT" == *"/$CMD"* ]]; then
    DETECTED="$CMD"
    IS_SPECIAL_CMD=true
    break
  fi
done

# If not special command, check regular personas
if [[ -z "$DETECTED" ]]; then
  for P in "${PERSONAS[@]}"; do
    if [[ "$INPUT" == *"/$P"* ]]; then
      DETECTED="$P"
      IS_SPECIAL_CMD=false
      break
    fi
  done
fi

DELEGATE_FLAG=""
if [[ "$INPUT" == *"/delegate"* ]]; then
  INPUT="${INPUT//\/delegate/}"
  DELEGATE_FLAG="--delegate-reasoning"
fi

if [[ -n "$DETECTED" ]]; then
  # Resolve paths
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  PROJECT_ROOT="${SCRIPT_DIR%/.cursor/commands/super-prompt}"

  if [[ "$IS_SPECIAL_CMD" == true ]]; then
    # Handle special initialization commands
    case "$DETECTED" in
      "init-sp")
        MODE="init"
        ;;
      "re-init-sp")
        MODE="reinit"
        ;;
    esac

    INIT_SCRIPT="$PROJECT_ROOT/.super-prompt/utils/init/init_sp.py"
    if command -v python3 >/dev/null 2>&1 && [[ -f "$INIT_SCRIPT" ]]; then
      echo "-------- Special command /$DETECTED detected — executing initialization script"
      exec python3 "$INIT_SCRIPT" --mode "$MODE"
    else
      echo "❌ Python3 not found or init script missing: $INIT_SCRIPT"
      exit 1
    fi
  else
    # Handle regular personas
    CLEANED_INPUT="${INPUT//\/$DETECTED/}"
    PROCESSOR_PATH="$PROJECT_ROOT/.super-prompt/utils/cursor-processors/enhanced_persona_processor.py"

    if command -v python3 >/dev/null 2>&1 && [[ -f "$PROCESSOR_PATH" ]]; then
      echo "-------- Persona detected: /$DETECTED — executing Python processor"
      exec python3 "$PROCESSOR_PATH" --persona "$DETECTED" --user-input "$CLEANED_INPUT" $DELEGATE_FLAG
    fi
  fi
fi

# Fallback: enforce Python core CLI directly (no Node fallback)
# Resolve project root (prefer git toplevel; fallback to CWD)
resolve_project_root() {
  if command -v git >/dev/null 2>&1; then
    if GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null); then
      printf "%s" "$GIT_ROOT"
      return 0
    fi
  fi
  printf "%s" "$(pwd)"
}

PROJECT_ROOT="$(resolve_project_root)"
PROJECT_CLI="$PROJECT_ROOT/.super-prompt/cli.py"

if [[ -f "$PROJECT_CLI" ]]; then
  echo "-------- No persona or processor unavailable — using project Python CLI"
  exec python3 "$PROJECT_CLI" optimize "$@"
fi

# Last resort: use installed wrapper if available (still executes Python)
if command -v super-prompt >/dev/null 2>&1; then
  echo "-------- Using installed super-prompt wrapper as fallback"
  exec super-prompt optimize "$@"
fi

echo "❌ Unable to locate Python CLI (.super-prompt/cli.py) or installed 'super-prompt'"
exit 1
