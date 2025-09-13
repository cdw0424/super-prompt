#!/usr/bin/env python3
"""
Super Prompt Emergency Recovery
Run this script if processors stop working
"""

import os
import sys
from pathlib import Path

def emergency_recovery():
    script_dir = Path(__file__).parent
    
    print("🚨 Super Prompt Emergency Recovery")
    print("=" * 40)
    
    # Fix permissions
    processor_files = [
        'codex-processor.py', 'high-processor.py', 'seq-processor.py',
        'seq-ultra-processor.py', 'architect-processor.py', 
        'analyzer-processor.py', 'frontend-processor.py', 'backend-processor.py'
    ]
    
    fixed = 0
    for filename in processor_files:
        file_path = script_dir / filename
        if file_path.exists():
            try:
                os.chmod(file_path, 0o755)
                print(f"✅ Fixed: {filename}")
                fixed += 1
            except Exception as e:
                print(f"❌ Error: {filename} - {e}")
    
    print(f"\n🔧 Fixed {fixed} files")
    
    # Test basic functionality
    try:
        import subprocess
        result = subprocess.run([sys.executable, "analyzer-processor.py"], 
                              cwd=str(script_dir), capture_output=True, timeout=5)
        if result.returncode == 1:
            print("✅ Processors responding")
        else:
            print("❌ Processors not responding properly")
    except:
        print("❌ Processor test failed")
    
    print("\n💡 If issues persist, run: python3 health-check.py")

if __name__ == "__main__":
    emergency_recovery()
