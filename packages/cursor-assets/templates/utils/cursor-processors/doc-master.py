#!/usr/bin/env python3
"""
Doc Master Persona Command - Cursor Wrapper
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
        '--persona', 'doc-master',
        ' '.join(sys.argv[1:]) if sys.argv[1:] else 'Please provide the topic or codebase that needs documentation. I will create clear and comprehensive technical documentation.'
    ], check=False)

if __name__ == "__main__":
    main()
