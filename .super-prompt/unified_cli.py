#!/usr/bin/env python3
"""
Super Prompt - Unified CLI Entry Point
Serves as the single entry point for both Codex and Cursor integrations.
Automatically detects the calling environment and routes accordingly.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Unified entry point for all Super Prompt CLI operations"""

    # Handle version request immediately
    if len(sys.argv) > 1 and sys.argv[1] in ['--version', '-v', 'version']:
        print("Super Prompt Unified CLI v3.1.70-unified")
        print("🔧 Enhanced CLI with .super-prompt/ tools integration for both Codex and Cursor")
        sys.exit(0)

    # Get the directory containing this script
    script_dir = Path(__file__).parent

    # Determine if we're being called from Codex or Cursor context
    calling_context = detect_calling_context()

    print(f"🚀 Super Prompt Unified CLI v3.1.70")
    print(f"🎯 Context: {calling_context}")

    # Route to appropriate CLI implementation
    if calling_context in ['codex', 'command-line', 'script']:
        # Use the enhanced CLI
        enhanced_cli = script_dir / 'enhanced_cli.py'
        if enhanced_cli.exists():
            print(f"🔧 Using Enhanced CLI: {enhanced_cli}")
            os.execv(sys.executable, [sys.executable, str(enhanced_cli)] + sys.argv[1:])
        else:
            print(f"❌ Enhanced CLI not found: {enhanced_cli}")
            sys.exit(1)

    elif calling_context == 'cursor':
        # Use the main Python package CLI for Cursor
        try:
            from super_prompt.cli import main as core_main
            print(f"🔧 Using Core Python CLI for Cursor")
            core_main()
        except ImportError:
            # Fallback to project-local CLI
            local_cli = script_dir / 'cli.py'
            if local_cli.exists():
                print(f"🔧 Using Local CLI fallback: {local_cli}")
                os.execv(sys.executable, [sys.executable, str(local_cli)] + sys.argv[1:])
            else:
                print(f"❌ No CLI implementation found")
                sys.exit(1)

    else:
        # Unknown context - default to Enhanced CLI
        print(f"⚠️ Unknown context, defaulting to Enhanced CLI")
        enhanced_cli = script_dir / 'enhanced_cli.py'
        if enhanced_cli.exists():
            os.execv(sys.executable, [sys.executable, str(enhanced_cli)] + sys.argv[1:])
        else:
            print(f"❌ Default CLI not found: {enhanced_cli}")
            sys.exit(1)

def detect_calling_context():
    """Detect whether we're being called from Codex, Cursor, or command line"""

    # Check environment variables
    if os.getenv('CODEX_MODE'):
        return 'codex'

    if os.getenv('CURSOR_MODE'):
        return 'cursor'

    # Check command line arguments for context hints
    args = ' '.join(sys.argv)
    if '/seq' in args or '/seq-ultra' in args or any(tag in args for tag in ['/frontend', '/backend', '/architect']):
        return 'codex'  # Tag-based execution typically from Codex

    # Check parent process or calling directory
    try:
        import psutil
        parent = psutil.Process(os.getppid())
        parent_name = parent.name().lower()

        if 'codex' in parent_name:
            return 'codex'
        elif 'cursor' in parent_name or 'code' in parent_name:
            return 'cursor'
    except ImportError:
        pass  # psutil not available, skip process detection
    except Exception:
        pass  # Process detection failed, skip

    # Check working directory for hints
    cwd = os.getcwd()
    if '.cursor' in cwd:
        return 'cursor'

    # Default detection based on available tools
    if os.path.exists('.cursor'):
        return 'cursor'

    return 'command-line'

if __name__ == "__main__":
    main()