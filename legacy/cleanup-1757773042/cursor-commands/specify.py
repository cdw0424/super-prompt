#!/usr/bin/env python3
"""
Specify Command - Create Feature Specification
SDD workflow integration
"""

import subprocess
import sys
import os

def main():
    # Path to the SDD processor
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..', '..')
    processor_path = os.path.join(project_root, '.super-prompt', 'utils', 'sdd', 'specify_processor.py')

    # Execute the SDD processor
    subprocess.run([
        'python3', processor_path
    ] + sys.argv[1:], check=False)

if __name__ == "__main__":
    main()
