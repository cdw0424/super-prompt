#!/usr/bin/env python3
"""
Plan Command - Create Implementation Plan
Enhanced based on Spec Kit v0.0.20 principles
"""

import subprocess
import sys
import os

def main():
    # Path to the actual plan processor in utils
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..', '..')
    processor_path = os.path.join(project_root, '.super-prompt', 'utils', 'sdd', 'plan_processor.py')

    # Execute the actual processor
    subprocess.run([
        'python3', processor_path
    ] + sys.argv[1:], check=False)

if __name__ == "__main__":
    main()
