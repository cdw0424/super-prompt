#!/usr/bin/env python3
"""
Grok Code Fast 1 Command - Cursor Wrapper
Leverages the enhanced 'dev' persona, while injecting Grok-optimized guidance.

Notes:
- No API key required: this is tuned for Cursor with Grok selected.
- Keeps prompts stable and structured to maximize cache hits.
"""

import subprocess
import sys
import os


def _build_grok_prefix() -> str:
    return (
        "# MODEL: Grok Code Fast 1 (Cursor)\n"
        "- Use native tool-calling; avoid XML wrappers.\n"
        "- Prefer multiple small, focused tool steps.\n"
        "- Keep section headers stable to improve cache hits.\n"
        "- English-only; mask secrets like sk-***.\n"
        "\n"
        "## GOALS\n"
        "- Clearly list goals and constraints.\n"
        "\n"
        "## CONTEXT\n"
        "- Reference exact file paths and only relevant snippets.\n"
        "\n"
        "## PLAN\n"
        "- Short, actionable steps (no stalling).\n"
        "\n"
        "## EXECUTE\n"
        "- Apply minimal diffs and exact zsh commands where relevant.\n"
        "\n"
        "## VERIFY\n"
        "- How to run and validate changes.\n"
    )


def main():
    # Use enhanced persona processor, targeting the general 'dev' persona
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..', '..')
    processor_path = os.path.join(project_root, '.super-prompt', 'utils', 'cursor-processors', 'enhanced_persona_processor.py')

    user_tail = ' '.join(sys.argv[1:]) if sys.argv[1:] else 'Optimize this task for Grok Code Fast 1.'
    full_input = _build_grok_prefix() + "\n\n" + user_tail

    print("-------- Grok mode: optimized for grok-code-fast-1 in Cursor")
    subprocess.run([
        'python3', processor_path,
        '--persona', 'dev',
        full_input
    ], check=False)


if __name__ == "__main__":
    main()

