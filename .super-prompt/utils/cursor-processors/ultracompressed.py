#!/usr/bin/env python3
"""
Ultracompressed Persona Command - Cursor Wrapper
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
        '--persona', 'ultracompressed',
        ' '.join(sys.argv[1:]) if sys.argv[1:] else 'Provide the information to be compressed. I will return the most concise representation.'
    ], check=False)

if __name__ == "__main__":
    main()
