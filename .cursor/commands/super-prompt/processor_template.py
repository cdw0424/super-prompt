#!/usr/bin/env python3
"""
Universal Processor Template
Stable subprocess-based execution for all super-prompt persona processors
"""

import os
import sys
import subprocess
from pathlib import Path

class ProcessorBase:
    """Base class for all persona processors with stable execution"""
    
    def __init__(self, persona_name: str, persona_icon: str, description: str, best_for: list):
        self.persona_name = persona_name
        self.persona_icon = persona_icon
        self.description = description
        self.best_for = best_for
        self.script_dir = Path(__file__).parent
        self.codex_processor_path = self.script_dir / "codex-processor.py"
    
    def show_usage(self, script_name: str):
        """Display usage information"""
        print(f"❌ Usage: {script_name} \"your question or request\"")
        print(f"\n{self.persona_icon} {self.persona_name}")
        print(f"   {self.description}")
        print("\n📋 Best for:")
        for item in self.best_for:
            print(f"   - {item}")
    
    def validate_codex_processor(self):
        """Validate that codex-processor.py exists and is executable"""
        if not self.codex_processor_path.exists():
            print("❌ Error: codex-processor.py not found")
            print(f"   Expected location: {self.codex_processor_path}")
            return False
        
        if not os.access(self.codex_processor_path, os.X_OK):
            print("❌ Error: codex-processor.py is not executable")
            print(f"   Run: chmod +x {self.codex_processor_path}")
            return False
        
        return True
    
    def execute(self, persona_key: str, user_input: str):
        """Execute the persona processor via subprocess"""
        
        # Validate prerequisites
        if not self.validate_codex_processor():
            return 1
        
        # Prepare command
        cmd = [sys.executable, str(self.codex_processor_path), persona_key, user_input]
        
        # Execute with proper error handling
        try:
            if os.environ.get('SP_DEBUG'):
                print(f"DEBUG: Executing {' '.join(cmd)}")
                print(f"DEBUG: Working directory {self.script_dir}")
            
            result = subprocess.run(
                cmd, 
                cwd=str(self.script_dir),
                env=os.environ.copy()  # Preserve environment variables
            )
            
            return result.returncode
            
        except FileNotFoundError as e:
            print(f"❌ Error: Required file not found - {e}")
            print("   Ensure all processor files are properly installed")
            return 1
            
        except PermissionError as e:
            print(f"❌ Error: Permission denied - {e}")
            print("   Check file permissions and executable status")
            return 1
            
        except Exception as e:
            print(f"❌ Error: Failed to execute processor - {e}")
            print("   Check system configuration and dependencies")
            return 1
    
    def main(self, args: list, persona_key: str, script_name: str):
        """Main entry point for persona processors"""
        
        if len(args) < 2:
            self.show_usage(script_name)
            return 1
        
        user_input = " ".join(args[1:]).strip()
        
        if not user_input:
            print("❌ Error: Please provide a non-empty question or request")
            return 1
        
        return self.execute(persona_key, user_input)


def create_processor(persona_name: str, persona_icon: str, description: str, best_for: list, persona_key: str):
    """Factory function to create a processor main function"""
    
    def main(args):
        processor = ProcessorBase(persona_name, persona_icon, description, best_for)
        script_name = f"{persona_key}-processor.py"
        return processor.main(args, persona_key, script_name)
    
    return main