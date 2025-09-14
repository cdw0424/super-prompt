#!/usr/bin/env python3
"""
Seq Persona Command - Cursor Wrapper
Enhanced based on LLM coding assistant research
"""

import subprocess
import sys
import os

def main():
    print("🚀 SEQ PERSONA - SEQUENTIAL CHAIN-OF-THOUGHT MODE")

    # Get user input
    user_input = ' '.join(sys.argv[1:]) if sys.argv[1:] else 'Ready to execute a sequence of tasks. Please provide the steps.'

    # Use the dedicated Sequential COT Engine for forced chain-of-thought
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cot_engine_path = os.path.join(script_dir, 'seq_cot_engine.py')

    if os.path.exists(cot_engine_path):
        print("🧠 Activating Sequential Chain-of-Thought Engine...")
        # Execute the COT engine with immediate execution
        subprocess.run([
            'python3', cot_engine_path, user_input
        ], check=False)
    else:
        print("❌ Sequential COT Engine not found, falling back to enhanced processor...")
        # Fallback to enhanced persona processor
        project_root = os.path.join(script_dir, '..', '..', '..')
        processor_path = os.path.join(project_root, '.super-prompt', 'utils', 'cursor-processors', 'enhanced_persona_processor.py')

        subprocess.run([
            'python3', processor_path,
            '--persona', 'seq',
            user_input
        ], check=False)

if __name__ == "__main__":
    main()
