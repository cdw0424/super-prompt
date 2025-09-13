#!/usr/bin/env python3
"""
Technical Analyst Persona Command
Enhanced based on LLM coding assistant research
"""

import subprocess
import sys
import os

def main():
    # Use enhanced persona processor
    processor_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                  '.super-prompt', 'utils', 'cursor-processors',
                                  'enhanced_persona_processor.py')

    subprocess.run([
        'python3', processor_path,
        '--persona', 'analyzer',
        '--user-input', ' '.join(sys.argv[1:]) if sys.argv[1:] else 'Hello! How can I help you today?'
    ], check=False)

if __name__ == "__main__":
    main()
