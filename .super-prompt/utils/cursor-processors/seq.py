#!/usr/bin/env python3
"""
Seq Persona Command - Cursor Wrapper
Enhanced based on LLM coding assistant research
"""

import subprocess
import sys
import os

def main():
    # Use enhanced persona processor for all personas
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..', '..')
    processor_path = os.path.join(project_root, '.super-prompt', 'utils', 'cursor-processors', 'enhanced_persona_processor.py')

    # Execute the enhanced persona processor
    subprocess.run([
        'python3', processor_path,
        '--persona', 'seq',
        '--user-input', ' '.join(sys.argv[1:]) if sys.argv[1:] else 'Hello! How can I help you today?'
    ], check=False)

if __name__ == "__main__":
    main()
