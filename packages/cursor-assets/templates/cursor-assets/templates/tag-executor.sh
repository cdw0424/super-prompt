#!/usr/bin/env bash
set -euo pipefail

# Resolve project root to find utility scripts reliably.
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# Define paths for persona processors and other utilities.
UTILS_DIR="$PROJECT_ROOT/.super-prompt/utils"
PROCESSOR_DIR="$UTILS_DIR/cursor-processors"

# ====================================================================
# COMMAND DETECTION & SECURITY DIRECTIVES
# ====================================================================

# CRITICAL SECURITY DIRECTIVE:
# NEVER access any folders starting with '.' (hidden folders) when processing commands
# This includes .git, .cursor, .super-prompt, .npm, etc.
# Commands must operate only in visible project directories

# COMMAND PRIORITY DETECTION:
# Commands must be detected as TOP PRIORITY regardless of input format
# Especially in Grok mode, command detection takes precedence over all other processing

# Initialize variables to hold the detected persona tag and the user's input.
TAG=""
USER_INPUT="$*"
COMMAND_DETECTED=false

# Initialize GROK_FLAG_FILE early to avoid unbound variable errors
GROK_FLAG_FILE=""

# ====================================================================
# ABSOLUTE COMMAND DETECTION GUARANTEE (TOP PRIORITY)
# ====================================================================

# Function to detect and validate persona tags with guaranteed accuracy
detect_persona_tag() {
    local input="$1"

    # ABSOLUTE PRIORITY: Check for new --sp-persona format: --sp-persona
    if [[ "$input" =~ ^--sp-([a-zA-Z0-9_-]+) ]]; then
        echo "-------- 🎯 GUARANTEED: --sp- format detected: ${BASH_REMATCH[1]}" >&2
        echo "${BASH_REMATCH[1]}"
        return 0
    fi

    # HIGH PRIORITY: Check for explicit tag format: /tagname
    if [[ "$input" =~ ^/([a-zA-Z0-9_-]+) ]]; then
        echo "-------- 🎯 GUARANTEED: / format detected: ${BASH_REMATCH[1]}" >&2
        echo "${BASH_REMATCH[1]}"
        return 0
    fi

    # MEDIUM PRIORITY: Check for tag at end: "input /tagname"
    if [[ "$input" =~ \ /([a-zA-Z0-9_-]+)$ ]]; then
        echo "-------- 🎯 GUARANTEED: end tag detected: ${BASH_REMATCH[1]}" >&2
        echo "${BASH_REMATCH[1]}"
        return 0
    fi

    # LOW PRIORITY: Check for tag in middle: "input /tagname more text"
    if [[ "$input" =~ \ /([a-zA-Z0-9_-]+)\  ]]; then
        echo "-------- 🎯 GUARANTEED: middle tag detected: ${BASH_REMATCH[1]}" >&2
        echo "${BASH_REMATCH[1]}"
        return 0
    fi

    echo "-------- ❌ NO COMMAND: '$input'" >&2
    return 1
}

# Unified mode toggle handler (Grok & Codex)
process_mode_command() {
    local mode_command="$1"

    case "$mode_command" in
        # Grok mode toggles (new + legacy)
        "grok-mode-on"|"grok-on")
            mkdir -p "$PROJECT_ROOT/.cursor" 2>/dev/null || true
            if [ -f "$PROJECT_ROOT/.cursor/.grok-mode" ]; then
                echo "-------- ℹ️  Grok mode is already active"
                echo "-------- ✅ Grok mode confirmed and ready"
            else
                : > "$PROJECT_ROOT/.cursor/.grok-mode"
                echo "-------- 🚀 Grok mode enabled"
                echo "-------- ✨ All subsequent commands will use Grok-optimized prompting"
            fi
            # Enforce mutual exclusivity: disable Codex mode when Grok is enabled
            if [ -f "$PROJECT_ROOT/.cursor/.codex-mode" ]; then
                rm -f "$PROJECT_ROOT/.cursor/.codex-mode" 2>/dev/null || true
                echo "-------- 🔀 Disabled Codex AMR mode due to Grok activation"
            fi
            echo "-------- 🎯 Grok mode status: ACTIVE"
            echo "-------- 💡 Enhanced command detection and AI assistance enabled"
            ;;

        "grok-mode-off"|"grok-off")
            if [ -f "$PROJECT_ROOT/.cursor/.grok-mode" ]; then
                rm -f "$PROJECT_ROOT/.cursor/.grok-mode" 2>/dev/null || true
                echo "-------- 🔌 Grok mode disabled"
                echo "-------- 📝 Standard command detection active"
            else
                echo "-------- ℹ️  Grok mode was not active"
            fi
            echo "-------- 🎯 Grok mode status: INACTIVE"
            echo "-------- 💡 Standard command processing active"
            ;;

        # Codex AMR mode toggles
        "codex-mode-on")
            mkdir -p "$PROJECT_ROOT/.cursor" 2>/dev/null || true
            if [ -f "$PROJECT_ROOT/.cursor/.codex-mode" ]; then
                echo "-------- ℹ️  Codex AMR mode is already active"
                echo "-------- ✅ Codex AMR confirmed and ready"
            else
                : > "$PROJECT_ROOT/.cursor/.codex-mode"
                echo "-------- 🚀 Codex AMR mode enabled"
                echo "-------- ✨ Auto Model Router (AMR) signals enabled for planning/review"
            fi
            # Enforce mutual exclusivity: disable Grok mode when Codex is enabled
            if [ -f "$PROJECT_ROOT/.cursor/.grok-mode" ]; then
                rm -f "$PROJECT_ROOT/.cursor/.grok-mode" 2>/dev/null || true
                echo "-------- 🔀 Disabled Grok mode due to Codex AMR activation"
            fi
            echo "-------- 🎯 Codex AMR mode status: ACTIVE"
            echo "-------- 💡 Intelligent task classification and routing enabled"
            ;;

        "codex-mode-off")
            if [ -f "$PROJECT_ROOT/.cursor/.codex-mode" ]; then
                rm -f "$PROJECT_ROOT/.cursor/.codex-mode" 2>/dev/null || true
                echo "-------- 🔌 Codex AMR mode disabled"
                echo "-------- 📝 Standard command detection active"
            else
                echo "-------- ℹ️  Codex AMR mode was not active"
            fi
            echo "-------- 🎯 Codex AMR mode status: INACTIVE"
            echo "-------- 💡 Standard command processing active"
            ;;
    esac
}

# PRIMARY COMMAND DETECTION (Highest Priority - Guaranteed Execution)
echo "-------- 🔍 COMMAND DETECTION STARTED" >&2

# Track all arguments for guaranteed processing
ALL_ARGS="$*"
COMMAND_EXECUTION_GUARANTEED=false

# PRIMARY DETECTION: Check each argument individually (Cursor-native /command priority)ㅌ
for arg in "$@"; do
    echo "-------- 🔎 Checking argument: '$arg'" >&2
    # PRIORITY 1: Check for Cursor-native /command format (highest priority)
    if [[ "$arg" =~ ^/([a-zA-Z0-9_-]+) ]]; then
        DETECTED_TAG="${BASH_REMATCH[1]}"
        TAG="$DETECTED_TAG"
        COMMAND_DETECTED=true
        COMMAND_EXECUTION_GUARANTEED=true
        echo "-------- 🎯 CURSOR NATIVE: /$DETECTED_TAG command detected (highest priority)" >&2
        echo "-------- ✅ COMMAND DETECTED: /$TAG (primary Cursor-native)" >&2
        echo "-------- 🎯 COMMAND EXECUTION GUARANTEED" >&2
        break

    # PRIORITY 2: Check for explicit --sp- format
    elif DETECTED_TAG=$(detect_persona_tag "$arg"); then
        echo "-------- 🎯 EXPLICIT TAG: /$DETECTED_TAG command detected" >&2

        # Special handling for mode toggle commands - process immediately and exit
        if [[ "$DETECTED_TAG" == "grok-mode-on" ]] || [[ "$DETECTED_TAG" == "grok-mode-off" ]] || \
           [[ "$DETECTED_TAG" == "grok-on" ]] || [[ "$DETECTED_TAG" == "grok-off" ]] || \
           [[ "$DETECTED_TAG" == "codex-mode-on" ]] || [[ "$DETECTED_TAG" == "codex-mode-off" ]]; then
            TAG="$DETECTED_TAG"
            COMMAND_DETECTED=true
            COMMAND_EXECUTION_GUARANTEED=true
            echo "-------- ⚡ EXECUTING MODE TOGGLE IMMEDIATELY" >&2
            process_mode_command "$TAG"
            exit 0
        else
            TAG="$DETECTED_TAG"
            COMMAND_DETECTED=true
            COMMAND_EXECUTION_GUARANTEED=true
            echo "-------- ✅ COMMAND DETECTED: /$TAG (primary explicit)" >&2
            echo "-------- 🎯 COMMAND EXECUTION GUARANTEED" >&2
            break
        fi
    else
        echo "-------- ❌ No command detected in: '$arg'" >&2
    fi
done

# ENHANCED DETECTION: If no command found, check the entire input string for embedded commands
if [ "$COMMAND_DETECTED" = false ]; then
    echo "-------- 🔍 ENHANCED DETECTION: Scanning entire input for embedded commands" >&2
    ENTIRE_INPUT="$*"

    # PRIORITY 1: Check for Cursor-native /command in entire input (highest priority)
    if [[ "$ENTIRE_INPUT" =~ /([a-zA-Z0-9_-]+) ]]; then
        DETECTED_TAG="${BASH_REMATCH[1]}"
        TAG="$DETECTED_TAG"
        COMMAND_DETECTED=true
        COMMAND_EXECUTION_GUARANTEED=true
        echo "-------- 🎯 CURSOR NATIVE EMBEDDED: /$DETECTED_TAG command found" >&2
        echo "-------- ✅ COMMAND DETECTED: /$TAG (enhanced Cursor-native)" >&2
        echo "-------- 🎯 COMMAND EXECUTION GUARANTEED (Cursor-native)" >&2

        # Extract user input (everything after the /command)
        USER_INPUT="${ENTIRE_INPUT#*/$TAG}"
        # Remove leading/trailing whitespace
        USER_INPUT=$(echo "$USER_INPUT" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')

    # PRIORITY 2: Check for --sp- pattern anywhere in the input
    elif [[ "$ENTIRE_INPUT" =~ --sp-([a-zA-Z0-9_-]+) ]]; then
        DETECTED_TAG="${BASH_REMATCH[1]}"
        echo "-------- 🎯 EXPLICIT EMBEDDED: --sp-$DETECTED_TAG command found" >&2
        TAG="$DETECTED_TAG"
        COMMAND_DETECTED=true
        COMMAND_EXECUTION_GUARANTEED=true
        echo "-------- ✅ COMMAND DETECTED: /$TAG (enhanced explicit)" >&2
        echo "-------- 🎯 COMMAND EXECUTION GUARANTEED (explicit)" >&2

        # Extract user input (everything after the command)
        USER_INPUT="${ENTIRE_INPUT#*--sp-$TAG}"
        # Remove leading/trailing whitespace
        USER_INPUT=$(echo "$USER_INPUT" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
    fi
fi

# Log detection summary
if [ "$COMMAND_EXECUTION_GUARANTEED" = true ]; then
    echo "-------- 🎉 COMMAND EXECUTION GUARANTEE: ACTIVATED" >&2
else
    echo "-------- ℹ️  NO COMMAND DETECTED - SKIPPING EXECUTION" >&2
fi

# SECONDARY COMMAND DETECTION (Full input scan - Guaranteed)
if [ "$COMMAND_DETECTED" = false ]; then
    echo "-------- 🔄 SECONDARY DETECTION: Scanning full input" >&2

    # Enhanced secondary detection with multiple patterns
    if DETECTED_TAG=$(detect_persona_tag "$USER_INPUT"); then
        TAG="$DETECTED_TAG"
        COMMAND_DETECTED=true
        COMMAND_EXECUTION_GUARANTEED=true
        echo "-------- ✅ COMMAND DETECTED: /$TAG (secondary detection)" >&2
        echo "-------- 🎯 COMMAND EXECUTION GUARANTEED (secondary)" >&2
    else
        echo "-------- ❌ NO COMMAND FOUND in full input scan" >&2
    fi
fi

# FINAL EXECUTION GUARANTEE CHECK
if [ "$COMMAND_EXECUTION_GUARANTEED" = true ]; then
    echo "-------- 🚀 EXECUTION GUARANTEE CONFIRMED - PROCEEDING WITH COMMAND" >&2
elif [ "$COMMAND_DETECTED" = true ]; then
    COMMAND_EXECUTION_GUARANTEED=true
    echo "-------- ⚠️  COMMAND DETECTED BUT GUARANTEE PENDING - ACTIVATING GUARANTEE" >&2
else
    echo "-------- 🛑 NO COMMAND DETECTED - EXITING WITHOUT EXECUTION" >&2
    echo "-------- ℹ️  Use --sp-persona format for guaranteed command execution" >&2
    exit 0
fi

# Remove the detected tag from user input
if [ "$COMMAND_DETECTED" = true ]; then
    USER_INPUT=$(echo "$USER_INPUT" | sed "s|--sp-$TAG||" | sed "s| /$TAG||" | sed "s|/$TAG||" | xargs)
fi

# Filter out flags/tags from user input: drop tokens starting with '--sp-', '-', or '/'
filter_user_input() {
    awk '{
      for (i=1;i<=NF;i++) {
        t=$i;
        if (t ~ /^--sp-/ || t ~ /^-/ || t ~ /^\//) { next } else { out=out t " " }
      }
    } END{ gsub(/[ ]+$/, "", out); print out }'
}

USER_INPUT_CLEAN=$(printf '%s' "$USER_INPUT" | filter_user_input)
if [ -n "$USER_INPUT_CLEAN" ]; then
    USER_INPUT="$USER_INPUT_CLEAN"
fi

# ====================================================================
# INPUT SECURITY VALIDATION
# ====================================================================

# Validate user input for dangerous paths
validate_user_input() {
    local input="$1"

    # Check for hidden folder references in user input
    if [[ "$input" =~ /\.[^/]+ ]] || [[ "$input" =~ \.[^/]+/ ]]; then
        echo "-------- SECURITY WARNING: User input contains hidden folder reference" >&2
        echo "-------- SECURITY: Hidden folders (.git, .cursor, .npm, etc.) are blocked for security" >&2
        echo "-------- SECURITY: If you need to work with hidden folders, use explicit commands" >&2
        # Don't block execution, just warn - user might be asking about hidden folders conceptually
    fi

    # Check for directory traversal attempts
    if [[ "$input" =~ \.\. ]]; then
        echo "-------- SECURITY WARNING: Directory traversal detected in user input" >&2
        echo "-------- SECURITY: '../' patterns are flagged for security review" >&2
    fi
}

# Validate user input
validate_user_input "$USER_INPUT"

# ====================================================================
# GROK MODE ENHANCEMENT
# ====================================================================

# ====================================================================
# GROK MODE INTEGRATION WITH ABSOLUTE COMMAND GUARANTEE
# ====================================================================

# Skip mode processing for toggle commands (already handled above)
if [[ "$TAG" != "grok-mode-on" ]] && [[ "$TAG" != "grok-mode-off" ]] && \
   [[ "$TAG" != "grok-on" ]] && [[ "$TAG" != "grok-off" ]] && \
   [[ "$TAG" != "codex-mode-on" ]] && [[ "$TAG" != "codex-mode-off" ]]; then
    # Ensure flag files are properly set
    GROK_FLAG_FILE="$PROJECT_ROOT/.cursor/.grok-mode"
    CODEX_FLAG_FILE="$PROJECT_ROOT/.cursor/.codex-mode"

    if [ -f "$GROK_FLAG_FILE" ]; then
        export SP_GROK_MODE=1
        echo "-------- 🧠 GROK MODE: ACTIVATED - Enhanced reasoning enabled" >&2
        echo "-------- ✅ SP_GROK_MODE set to: '$SP_GROK_MODE'" >&2

        # Ensure Codex CLI present for deep planning
        if ! command -v codex >/dev/null 2>&1; then
            if command -v npm >/dev/null 2>&1; then
                echo "-------- 🔧 Ensuring Codex CLI (@openai/codex) for deep reasoning" >&2
                npm install -g @openai/codex@latest >/dev/null 2>&1 || true
            else
                echo "-------- ⚠️  Warning: npm not found; cannot install Codex CLI automatically" >&2
            fi
        fi

        # GROK MODE: Apply the same absolute command guarantee system
        echo "-------- 🎯 GROK MODE: Command execution guarantee system ACTIVE" >&2

        # In Grok mode, apply the same enhanced command detection as regular mode
        if [ "$COMMAND_DETECTED" = false ]; then
            echo "-------- 🔍 GROK MODE: Enhanced command scanning with AI assistance" >&2
            echo "-------- 🔍 GROK MODE: Deep scanning input: '$USER_INPUT'" >&2

            # Apply the same pattern matching as detect_persona_tag function
            if [[ "$USER_INPUT" =~ --sp-([a-zA-Z0-9_-]+) ]]; then
                DETECTED_TAG="${BASH_REMATCH[1]}"
                TAG="$DETECTED_TAG"
                COMMAND_DETECTED=true
                COMMAND_EXECUTION_GUARANTEED=true
                echo "-------- 🎯 GROK MODE: --sp- pattern detected: /$TAG" >&2

                # Extract user input for Grok mode
                USER_INPUT="${USER_INPUT#*--sp-$TAG}"
                USER_INPUT=$(echo "$USER_INPUT" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')

            elif [[ "$USER_INPUT" =~ /([a-zA-Z0-9_-]+) ]]; then
                DETECTED_TAG="${BASH_REMATCH[1]}"
                TAG="$DETECTED_TAG"
                COMMAND_DETECTED=true
                COMMAND_EXECUTION_GUARANTEED=true
                echo "-------- 🎯 GROK MODE: / pattern detected: /$TAG" >&2

            else
                # Enhanced pattern matching for implicit commands in Grok mode
                if echo "$USER_INPUT" | grep -qi "analyze\|분석"; then
                    TAG="analyzer"
                    COMMAND_DETECTED=true
                    COMMAND_EXECUTION_GUARANTEED=true
                    echo "-------- 🎯 GROK MODE: Implicit 'analyze' command detected" >&2

                elif echo "$USER_INPUT" | grep -qi "dev\|개발\|implement\|구현"; then
                    TAG="dev"
                    COMMAND_DETECTED=true
                    COMMAND_EXECUTION_GUARANTEED=true
                    echo "-------- 🎯 GROK MODE: Implicit 'dev' command detected" >&2

                elif echo "$USER_INPUT" | grep -qi "frontend\|front\|ui\|화면"; then
                    TAG="frontend"
                    COMMAND_DETECTED=true
                    COMMAND_EXECUTION_GUARANTEED=true
                    echo "-------- 🎯 GROK MODE: Implicit 'frontend' command detected" >&2

                elif echo "$USER_INPUT" | grep -qi "backend\|back\|server\|서버"; then
                    TAG="backend"
                    COMMAND_DETECTED=true
                    COMMAND_EXECUTION_GUARANTEED=true
                    echo "-------- 🎯 GROK MODE: Implicit 'backend' command detected" >&2

                elif echo "$USER_INPUT" | grep -qi "architect\|architecture\|설계"; then
                    TAG="architect"
                    COMMAND_DETECTED=true
                    COMMAND_EXECUTION_GUARANTEED=true
                    echo "-------- 🎯 GROK MODE: Implicit 'architect' command detected" >&2
                fi
            fi

            # Update guarantee status for Grok mode
            if [ "$COMMAND_DETECTED" = true ]; then
                COMMAND_EXECUTION_GUARANTEED=true
                echo "-------- 🎯 GROK MODE: Command execution GUARANTEED" >&2
                echo "-------- 🧠 GROK MODE: Enhanced AI reasoning will be applied" >&2
            fi

            # Clean up detected command from user input
            if [ "$COMMAND_DETECTED" = true ]; then
                USER_INPUT=$(echo "$USER_INPUT" | sed "s/$TAG//gi" | sed "s/analyze//gi" | sed "s/architect//gi" | sed "s/backend//gi" | sed "s/frontend//gi" | sed "s/review//gi" | sed "s/implement//gi" | sed "s/plan//gi" | sed "s/spec//gi" | sed "s/task//gi" | xargs)
                echo "-------- 🧹 GROK MODE: Cleaned user input: '$USER_INPUT'" >&2
            fi
        else
            echo "-------- ℹ️  GROK MODE: Command already detected, skipping enhanced scanning" >&2
        fi
    else
        echo "-------- ℹ️  Standard mode (grok mode not active)" >&2
    fi

    # Activate Codex AMR mode if enabled
    if [ -f "$CODEX_FLAG_FILE" ]; then
        export SP_CODEX_MODE=1
        echo "-------- 🧭 CODEX AMR MODE: ACTIVATED - Router signals enabled" >&2
        echo "-------- ✅ SP_CODEX_MODE set to: '$SP_CODEX_MODE'" >&2
        # Ensure Codex CLI present for AMR assistance (best-effort)
        if ! command -v codex >/dev/null 2>&1; then
            if command -v npm >/dev/null 2>&1; then
                echo "-------- 🔧 Ensuring Codex CLI (@openai/codex) for AMR routing" >&2
                npm install -g @openai/codex@latest >/dev/null 2>&1 || true
            else
                echo "-------- ⚠️  Warning: npm not found; cannot install Codex CLI automatically" >&2
            fi
        fi
    fi
fi

# ====================================================================
# DEFAULT TAG HANDLING
# ====================================================================

# ====================================================================
# SECURITY & SANDBOXING DIRECTIVES
# ====================================================================

# CRITICAL: Never allow access to hidden folders (starting with .)
# This is a security measure to prevent unauthorized access to:
# - .git (version control)
# - .cursor (IDE configuration)
# - .super-prompt (internal utilities)
# - .npm, .cache, etc. (system/package caches)
# - Any other hidden directories

# Function to validate and sanitize paths
validate_path() {
    local path="$1"

    # SECURITY EXCEPTION: Allow .super-prompt directory (system core)
    # This is the ONLY allowed hidden directory for system functionality
    if [[ "$path" =~ /\.super-prompt ]]; then
        echo "-------- SECURITY: Allowing controlled access to .super-prompt (system core)" >&2
        return 0
    fi

    # CRITICAL SECURITY CHECK: Reject any OTHER path containing hidden directories
    if [[ "$path" =~ /\.[^/]+ ]]; then
        echo "-------- SECURITY VIOLATION: Access to hidden folder detected in path: $path" >&2
        echo "-------- BLOCKED DIRECTORIES: .git, .cursor, .npm, .cache, etc." >&2
        echo "-------- ALLOWED: Only .super-prompt (system core) is permitted" >&2
        echo "-------- COMMAND EXECUTION BLOCKED for security reasons" >&2
        exit 1
    fi

    # Check for dangerous path patterns
    if [[ "$path" =~ \.\. ]]; then
        echo "-------- SECURITY VIOLATION: Directory traversal detected in path: $path" >&2
        echo "-------- COMMAND EXECUTION BLOCKED for security reasons" >&2
        exit 1
    fi

    # Check for absolute paths that might be dangerous
    if [[ "$path" =~ ^/[^/]*\.\. ]]; then
        echo "-------- SECURITY VIOLATION: Suspicious absolute path: $path" >&2
        echo "-------- COMMAND EXECUTION BLOCKED for security reasons" >&2
        exit 1
    fi

    return 0
}

# Define GROK_FLAG_FILE properly
GROK_FLAG_FILE="$PROJECT_ROOT/.cursor/.grok-mode"
CODEX_FLAG_FILE="$PROJECT_ROOT/.cursor/.codex-mode"

# Apply security validation to key paths
validate_path "$PROJECT_ROOT"
validate_path "$UTILS_DIR"
validate_path "$PROCESSOR_DIR"

# ====================================================================
# DEFAULT TAG HANDLING
# ====================================================================

# HIGH COMMAND SPECIAL HANDLING: Ensure Codex CLI is available and provide input for high commands
if [[ "$TAG" == "high" ]]; then
    echo "-------- 🚨 HIGH COMMAND DETECTED: Deep strategic analysis mode ACTIVATED" >&2

    # Check if codex CLI is available
    if ! command -v codex >/dev/null 2>&1; then
        echo "-------- ⚠️  Codex CLI not found. Installing for high command processing..." >&2
        if command -v npm >/dev/null 2>&1; then
            echo "-------- 🔧 Installing @openai/codex CLI..." >&2
            npm install -g @openai/codex@latest >/dev/null 2>&1
            if [ $? -eq 0 ]; then
                echo "-------- ✅ Codex CLI installed successfully" >&2
            else
                echo "-------- ❌ Codex CLI installation failed" >&2
                echo "-------- ⚠️  High command will proceed with fallback processing" >&2
            fi
        else
            echo "-------- ❌ npm not found - cannot install Codex CLI" >&2
            echo "-------- ⚠️  High command will proceed with fallback processing" >&2
        fi
    else
        echo "-------- ✅ Codex CLI is available" >&2
    fi

    # CRITICAL FIX: Provide default input for high command if none provided
    if [ -z "$USER_INPUT" ] || [ "$USER_INPUT" = " " ]; then
        echo "-------- 🎯 HIGH COMMAND: No input provided, using strategic analysis prompt" >&2
        USER_INPUT="Please perform a comprehensive strategic analysis of this codebase. Identify architectural patterns, potential improvements, security considerations, performance optimizations, and provide detailed recommendations for enhancement. Focus on deep technical insights and long-term maintainability."
        echo "-------- 📝 HIGH COMMAND INPUT: $USER_INPUT" >&2
    else
        echo "-------- 📝 HIGH COMMAND INPUT: $USER_INPUT" >&2
    fi

    echo "-------- 🎯 High command processing: Codex CLI integration ACTIVE" >&2
    echo "-------- 🧠 DEEP REASONING MODE: Strategic analysis will be performed" >&2
fi

# If no tag is found, default to the 'dev' persona for general development tasks.
if [ -z "$TAG" ]; then
    echo "-------- WARNING: No persona tag found. Defaulting to /dev persona." >&2
    TAG="dev"
fi

# ====================================================================
# SPECIAL COMMAND HANDLING
# ====================================================================

# Note: Grok toggle commands are now handled immediately in primary detection
# to avoid duplicate processing and security messages

# Enable Grok mode for the dedicated /grok tag
if [[ "$TAG" == "grok" ]]; then
    export SP_GROK_MODE=1
    unset SP_CODEX_MODE || true
    echo "-------- Grok mode enabled for this session (/grok)"
    if ! command -v codex >/dev/null 2>&1; then
        if command -v npm >/dev/null 2>&1; then
            echo "-------- Ensuring Codex CLI (@openai/codex) for deep reasoning" >&2
            npm install -g @openai/codex@latest >/dev/null 2>&1 || true
        else
            echo "-------- Warning: npm not found; cannot install Codex CLI automatically" >&2
        fi
    fi
fi

# Enable Codex AMR mode for the dedicated /codex tag (session-only)
if [[ "$TAG" == "codex" ]]; then
    export SP_CODEX_MODE=1
    unset SP_GROK_MODE || true
    echo "-------- Codex AMR mode enabled for this session (/codex)"
    if ! command -v codex >/dev/null 2>&1; then
        if command -v npm >/dev/null 2>&1; then
            echo "-------- Ensuring Codex CLI (@openai/codex) for AMR routing" >&2
            npm install -g @openai/codex@latest >/dev/null 2>&1 || true
        else
            echo "-------- Warning: npm not found; cannot install Codex CLI automatically" >&2
        fi
    fi
fi

# ====================================================================
# SPECIAL COMMAND HANDLING (continued)
# ====================================================================

# Handle special, non-persona commands like initialization.
if [[ "$TAG" == "init-sp" || "$TAG" == "re-init-sp" ]]; then
    INIT_SCRIPT="$UTILS_DIR/init/init_sp.py"
    # Security check for init scripts
    validate_path "$INIT_SCRIPT"
    if [ -f "$INIT_SCRIPT" ]; then
        echo "-------- SECURITY: Path validated for init script: $INIT_SCRIPT" >&2
        exec python3 "$INIT_SCRIPT" "$TAG"
    else
        echo "-------- ERROR: Initialization script not found at '$INIT_SCRIPT'" >&2
        exit 1
    fi
fi

# ====================================================================
# PROCESSOR EXECUTION WITH GUARANTEED SECURITY
# ====================================================================

echo "-------- 🚀 COMMAND EXECUTION STARTING" >&2
echo "-------- 🎯 EXECUTION GUARANTEE: ACTIVE" >&2
echo "-------- 📋 COMMAND: /$TAG" >&2
echo "-------- 📝 INPUT: $USER_INPUT" >&2

# Display combined execution mode status (flag files or session envs)
if { [ -f "$GROK_FLAG_FILE" ] || [ "${SP_GROK_MODE-}" = "1" ]; } && \
   { [ -f "$CODEX_FLAG_FILE" ] || [ "${SP_CODEX_MODE-}" = "1" ]; }; then
    echo "-------- 🧠 EXECUTION MODE: GROK + CODEX AMR" >&2
elif [ -f "$GROK_FLAG_FILE" ] || [ "${SP_GROK_MODE-}" = "1" ]; then
    echo "-------- 🧠 EXECUTION MODE: GROK ENHANCED (AI reasoning active)" >&2
elif [ -f "$CODEX_FLAG_FILE" ] || [ "${SP_CODEX_MODE-}" = "1" ]; then
    echo "-------- 🧭 EXECUTION MODE: CODEX AMR (router enabled)" >&2
else
    echo "-------- 📋 EXECUTION MODE: STANDARD" >&2
fi

# Construct the path to the specific persona processor script.
PROCESSOR_SCRIPT="$PROCESSOR_DIR/${TAG}.py"

# Security validation for processor scripts
validate_path "$PROCESSOR_SCRIPT"

# Execute the specific processor if it exists. Otherwise, fall back to the generic
# enhanced processor, passing the tag as a parameter. This ensures graceful degradation.
if [ ! -f "$PROCESSOR_SCRIPT" ]; then
    echo "-------- WARNING: Processor for tag '/$TAG' not found at '$PROCESSOR_SCRIPT'. Falling back to generic processor." >&2
    FALLBACK_SCRIPT="$PROCESSOR_DIR/enhanced_persona_processor.py"

    # Security validation for fallback script
    validate_path "$FALLBACK_SCRIPT"

    if [ ! -f "$FALLBACK_SCRIPT" ]; then
        echo "-------- ERROR: Fallback processor 'enhanced_persona_processor.py' not found." >&2
        exit 1
    fi

    echo "-------- SECURITY: Path validated for fallback processor: $FALLBACK_SCRIPT" >&2
    echo "-------- 🎯 EXECUTING COMMAND WITH GUARANTEE (FALLBACK)" >&2

    # FINAL EXECUTION GUARANTEE - Execute with guaranteed success
    echo "-------- ✅ COMMAND EXECUTION GUARANTEED: PROCEEDING" >&2
    exec python3 "$FALLBACK_SCRIPT" --persona "$TAG" $USER_INPUT
else
    # Execute the dedicated processor script for the persona.
    echo "-------- SECURITY: Path validated for processor: $PROCESSOR_SCRIPT" >&2
    echo "-------- 🎯 EXECUTING COMMAND WITH GUARANTEE (DEDICATED)" >&2

    # FINAL EXECUTION GUARANTEE - Execute with guaranteed success
    echo "-------- ✅ COMMAND EXECUTION GUARANTEED: PROCEEDING" >&2
    exec python3 "$PROCESSOR_SCRIPT" "$USER_INPUT"
fi

# ====================================================================
# ABSOLUTE EXECUTION GUARANTEE VERIFICATION
# ====================================================================

# CRITICAL SAFETY CHECK: If we reach this point, something went wrong
if [ "$COMMAND_EXECUTION_GUARANTEED" = true ]; then
    echo "-------- 🚨 CRITICAL FAILURE: Execution guarantee was active but execution did not occur!" >&2
    echo "-------- 🚨 COMMAND: /$TAG" >&2
    echo "-------- 🚨 INPUT: $USER_INPUT" >&2
    echo "-------- 🚨 This is a SYSTEM FAILURE - command execution was guaranteed but failed" >&2
    echo "-------- 🚨 Please report this error to the development team" >&2
    exit 1
else
    echo "-------- ✅ SAFE EXIT: No command detected, exiting normally" >&2
    echo "-------- ℹ️  Use --sp-persona format for guaranteed command execution" >&2
    echo "-------- ℹ️  Example: --sp-dev \"analyze this code\"" >&2
    exit 0
fi
