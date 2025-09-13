#!/usr/bin/env python3
"""
Auto-Setup and Recovery System
Automatically fixes common issues and ensures proper configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict

class AutoSetup:
    """Automatic setup and recovery for Super Prompt system"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.fixes_applied = []
        self.errors = []
    
    def log_fix(self, message: str):
        """Log a successful fix"""
        self.fixes_applied.append(message)
        print(f"🔧 {message}")
    
    def log_error(self, message: str):
        """Log an error"""
        self.errors.append(message)
        print(f"❌ {message}")
    
    def ensure_executable_permissions(self) -> int:
        """Ensure all processor files have executable permissions"""
        print("🔐 Setting executable permissions...")
        
        processor_files = [
            'codex-processor.py',
            'processor_template.py', 
            'high-processor.py',
            'seq-processor.py',
            'seq-ultra-processor.py',
            'architect-processor.py',
            'analyzer-processor.py',
            'frontend-processor.py',
            'backend-processor.py',
            'debate-processor.py',
            'health-check.py',
            'auto-setup.py'
        ]
        
        fixed_count = 0
        
        for filename in processor_files:
            file_path = self.script_dir / filename
            
            if file_path.exists():
                try:
                    # Set executable permissions
                    os.chmod(file_path, 0o755)
                    
                    # Verify permissions
                    if os.access(file_path, os.X_OK):
                        self.log_fix(f"Executable permissions: {filename}")
                        fixed_count += 1
                    else:
                        self.log_error(f"Failed to set executable: {filename}")
                except Exception as e:
                    self.log_error(f"Permission error for {filename}: {e}")
            else:
                self.log_error(f"File not found: {filename}")
        
        return fixed_count
    
    def create_required_directories(self) -> int:
        """Create required directories for logging and state"""
        print("📁 Creating required directories...")
        
        base_dir = Path(self.script_dir).parent.parent.parent  # Go up to project root
        
        required_dirs = [
            base_dir / ".cursor" / "logs" / "persona-sessions",
            base_dir / ".cursor" / "logs" / "high-analysis", 
            base_dir / ".cursor" / "logs" / "health-checks",
            base_dir / "debates" / "state"
        ]
        
        created_count = 0
        
        for dir_path in required_dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                self.log_fix(f"Directory created: {dir_path.relative_to(base_dir)}")
                created_count += 1
            except Exception as e:
                self.log_error(f"Failed to create directory {dir_path}: {e}")
        
        return created_count
    
    def validate_processor_template(self) -> bool:
        """Validate processor template is properly formatted"""
        print("📝 Validating processor template...")
        
        template_path = self.script_dir / "processor-template.py"
        
        if not template_path.exists():
            self.log_error("processor-template.py not found")
            return False
        
        try:
            # Test import
            import importlib.util
            spec = importlib.util.spec_from_file_location("processor_template", template_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check required functions exist
            required_attrs = ['ProcessorBase', 'create_processor']
            for attr in required_attrs:
                if not hasattr(module, attr):
                    self.log_error(f"Missing required attribute: {attr}")
                    return False
            
            self.log_fix("Processor template validation passed")
            return True
            
        except Exception as e:
            self.log_error(f"Processor template validation failed: {e}")
            return False
    
    def fix_import_paths(self) -> int:
        """Fix import path issues in processor files"""
        print("🔗 Fixing import paths...")
        
        fixed_count = 0
        
        # Files that should import from processor_template
        processor_files = [
            'seq-processor.py',
            'seq-ultra-processor.py',
            'architect-processor.py',
            'analyzer-processor.py',
            'frontend-processor.py',
            'backend-processor.py',
            'high-processor.py'
        ]
        
        for filename in processor_files:
            file_path = self.script_dir / filename
            
            if file_path.exists():
                try:
                    # Read file content
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Check if it has the correct import structure
                    if 'from processor_template import create_processor' in content:
                        self.log_fix(f"Import path OK: {filename}")
                        fixed_count += 1
                    else:
                        self.log_error(f"Import path needs fixing: {filename}")
                
                except Exception as e:
                    self.log_error(f"Error checking imports in {filename}: {e}")
        
        return fixed_count
    
    def test_processor_functionality(self) -> Dict[str, bool]:
        """Test each processor can execute without errors"""
        print("🧪 Testing processor functionality...")
        
        processors = {
            'seq': 'seq-processor.py',
            'seq-ultra': 'seq-ultra-processor.py',
            'architect': 'architect-processor.py',
            'analyzer': 'analyzer-processor.py',
            'frontend': 'frontend-processor.py',
            'backend': 'backend-processor.py',
            'high': 'high-processor.py',
            'debate': 'debate-processor.py'
        }
        
        results = {}
        
        for persona, filename in processors.items():
            try:
                # Test basic execution (should show usage)
                result = subprocess.run(
                    [sys.executable, filename],
                    cwd=str(self.script_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Expect usage message (return code 1)
                if result.returncode == 1 and "Usage:" in result.stdout:
                    self.log_fix(f"Processor test passed: {persona}")
                    results[persona] = True
                else:
                    self.log_error(f"Processor test failed: {persona}")
                    if result.stderr:
                        print(f"   Error: {result.stderr.strip()[:100]}...")
                    results[persona] = False
            
            except subprocess.TimeoutExpired:
                self.log_error(f"Processor test timeout: {persona}")
                results[persona] = False
            except Exception as e:
                self.log_error(f"Processor test error: {persona} - {e}")
                results[persona] = False
        
        return results
    
    def install_codex_cli_if_missing(self) -> bool:
        """Attempt to install Codex CLI if it's missing"""
        print("🤖 Checking Codex CLI installation...")
        
        if shutil.which("codex"):
            self.log_fix("Codex CLI already installed")
            return True
        
        # Check if npm is available
        if not shutil.which("npm"):
            self.log_error("npm not found - cannot auto-install Codex CLI")
            print("   Please install Node.js and npm first")
            return False
        
        print("   Installing Codex CLI...")
        try:
            result = subprocess.run(
                ["npm", "install", "-g", "@openai/codex@latest"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.log_fix("Codex CLI installed successfully")
                return True
            else:
                self.log_error("Codex CLI installation failed")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()[:200]}...")
                return False
        
        except subprocess.TimeoutExpired:
            self.log_error("Codex CLI installation timeout")
            return False
        except Exception as e:
            self.log_error(f"Codex CLI installation error: {e}")
            return False
    
    def create_recovery_script(self) -> bool:
        """Create a recovery script for common issues"""
        print("💾 Creating recovery script...")
        
        recovery_script = '''#!/usr/bin/env python3
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
    
    print(f"\\n🔧 Fixed {fixed} files")
    
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
    
    print("\\n💡 If issues persist, run: python3 health-check.py")

if __name__ == "__main__":
    emergency_recovery()
'''
        
        try:
            recovery_path = self.script_dir / "emergency-recovery.py"
            with open(recovery_path, 'w') as f:
                f.write(recovery_script)
            
            os.chmod(recovery_path, 0o755)
            self.log_fix("Emergency recovery script created")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to create recovery script: {e}")
            return False
    
    def run_full_setup(self) -> bool:
        """Run complete auto-setup process"""
        print("🚀 Super Prompt Auto-Setup")
        print("=" * 50)
        
        setup_tasks = [
            ("Executable Permissions", self.ensure_executable_permissions),
            ("Required Directories", self.create_required_directories),
            ("Processor Template", self.validate_processor_template),
            ("Import Paths", self.fix_import_paths),
            ("Recovery Script", self.create_recovery_script),
            ("Codex CLI", self.install_codex_cli_if_missing)
        ]
        
        all_success = True
        
        for task_name, task_func in setup_tasks:
            print(f"\n📋 {task_name}...")
            try:
                result = task_func()
                if isinstance(result, bool):
                    if not result:
                        all_success = False
                elif isinstance(result, int):
                    if result == 0:
                        print(f"   No changes needed for {task_name}")
            except Exception as e:
                self.log_error(f"{task_name} failed: {e}")
                all_success = False
        
        # Final functionality test
        print(f"\n🧪 Final Functionality Test...")
        test_results = self.test_processor_functionality()
        working_processors = sum(test_results.values())
        total_processors = len(test_results)
        
        print(f"\n📊 Setup Summary:")
        print(f"✅ {len(self.fixes_applied)} fixes applied")
        if self.errors:
            print(f"❌ {len(self.errors)} errors encountered")
        print(f"🎯 {working_processors}/{total_processors} processors functional")
        
        if working_processors == total_processors and len(self.errors) == 0:
            print("\n🎉 Auto-setup completed successfully!")
            print("   Super Prompt is ready for use")
            return True
        else:
            print("\n⚠️  Auto-setup completed with issues")
            print("   Run 'python3 health-check.py' for detailed diagnosis")
            return False

def main():
    """Auto-setup entry point"""
    setup = AutoSetup()
    
    success = setup.run_full_setup()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())