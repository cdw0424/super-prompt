#!/usr/bin/env python3
"""
Super Prompt Health Check and Environment Validation
Ensures all components are properly configured and executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Tuple, Dict

class HealthChecker:
    """Comprehensive health check for Super Prompt system"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.fixes_applied = []
    
    def log_issue(self, issue: str):
        """Log a critical issue"""
        self.issues.append(issue)
        print(f"❌ ISSUE: {issue}")
    
    def log_warning(self, warning: str):
        """Log a warning"""
        self.warnings.append(warning)
        print(f"⚠️  WARNING: {warning}")
    
    def log_fix(self, fix: str):
        """Log a fix that was applied"""
        self.fixes_applied.append(fix)
        print(f"🔧 FIXED: {fix}")
    
    def log_ok(self, message: str):
        """Log a successful check"""
        print(f"✅ OK: {message}")
    
    def check_python_environment(self) -> bool:
        """Check Python environment requirements"""
        print("\n🐍 Checking Python Environment...")
        
        # Check Python version
        if sys.version_info < (3, 7):
            self.log_issue(f"Python {sys.version_info.major}.{sys.version_info.minor} is too old. Requires Python 3.7+")
            return False
        else:
            self.log_ok(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        
        # Check required modules
        required_modules = ['subprocess', 'pathlib', 'json', 'os', 'sys']
        for module in required_modules:
            try:
                __import__(module)
                self.log_ok(f"Module '{module}' available")
            except ImportError:
                self.log_issue(f"Required module '{module}' not available")
                return False
        
        return True
    
    def check_core_files(self) -> bool:
        """Check that all core processor files exist and are valid"""
        print("\n📁 Checking Core Files...")
        
        core_files = [
            ('codex-processor.py', True),  # (filename, must_be_executable)
            ('processor_template.py', False),
            ('high-processor.py', True),
            ('seq-processor.py', True),
            ('seq-ultra-processor.py', True),
            ('architect-processor.py', True),
            ('analyzer-processor.py', True), 
            ('frontend-processor.py', True),
            ('backend-processor.py', True),
            ('debate-processor.py', True),
        ]
        
        all_ok = True
        
        for filename, must_be_executable in core_files:
            file_path = self.script_dir / filename
            
            if not file_path.exists():
                self.log_issue(f"Core file missing: {filename}")
                all_ok = False
                continue
            
            self.log_ok(f"File exists: {filename}")
            
            if must_be_executable and not os.access(file_path, os.X_OK):
                try:
                    os.chmod(file_path, 0o755)
                    self.log_fix(f"Made executable: {filename}")
                except Exception as e:
                    self.log_issue(f"Cannot make executable: {filename} - {e}")
                    all_ok = False
        
        return all_ok
    
    def check_codex_cli(self) -> bool:
        """Check Codex CLI availability"""
        print("\n🤖 Checking Codex CLI...")
        
        if not shutil.which("codex"):
            self.log_warning("Codex CLI not found in PATH. Complex reasoning will be limited.")
            print("   To install: npm install -g @openai/codex@latest")
            return False
        else:
            self.log_ok("Codex CLI found")
            
            # Test Codex CLI basic functionality
            try:
                result = subprocess.run(
                    ["codex", "--version"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode == 0:
                    self.log_ok("Codex CLI responsive")
                    return True
                else:
                    self.log_warning("Codex CLI not responding properly")
                    return False
            except Exception as e:
                self.log_warning(f"Codex CLI test failed: {e}")
                return False
    
    def check_processor_integrity(self) -> bool:
        """Test that processors can import template correctly"""
        print("\n🔄 Checking Processor Integrity...")
        
        processors = [
            'seq-processor.py',
            'seq-ultra-processor.py', 
            'architect-processor.py',
            'analyzer-processor.py',
            'frontend-processor.py',
            'backend-processor.py',
            'high-processor.py',
            'debate-processor.py'
        ]
        
        all_ok = True
        
        for processor in processors:
            try:
                # Test basic import and execution
                result = subprocess.run(
                    [sys.executable, processor],
                    cwd=str(self.script_dir),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Expect usage message (return code 1)
                if result.returncode == 1 and "Usage:" in result.stdout:
                    self.log_ok(f"Processor functional: {processor}")
                else:
                    self.log_issue(f"Processor not functional: {processor}")
                    if result.stderr:
                        print(f"   Error: {result.stderr.strip()}")
                    all_ok = False
                    
            except subprocess.TimeoutExpired:
                self.log_issue(f"Processor timeout: {processor}")
                all_ok = False
            except Exception as e:
                self.log_issue(f"Processor test failed: {processor} - {e}")
                all_ok = False
        
        return all_ok
    
    def check_cursor_integration(self) -> bool:
        """Check Cursor slash command integration"""
        print("\n🎯 Checking Cursor Integration...")
        
        cursor_dir = Path(self.script_dir).parent.parent.parent  # Go up to .cursor
        commands_dir = cursor_dir / "commands" / "super-prompt"
        
        if not commands_dir.exists():
            self.log_warning("Cursor commands directory not found")
            return False
        
        slash_commands = [
            'high.md', 'seq.md', 'seq-ultra.md', 'architect.md', 
            'analyzer.md', 'frontend.md', 'backend.md', 'debate.md'
        ]
        
        all_ok = True
        for cmd_file in slash_commands:
            cmd_path = commands_dir / cmd_file
            if cmd_path.exists():
                self.log_ok(f"Slash command: /{cmd_file[:-3]}")
            else:
                self.log_warning(f"Missing slash command: /{cmd_file[:-3]}")
                all_ok = False
        
        return all_ok
    
    def perform_auto_repair(self) -> bool:
        """Attempt to automatically fix common issues"""
        print("\n🔧 Performing Auto-Repair...")
        
        repairs_made = 0
        
        # Ensure all processor files are executable
        processor_files = [
            'codex-processor.py', 'high-processor.py', 'seq-processor.py',
            'seq-ultra-processor.py', 'architect-processor.py', 
            'analyzer-processor.py', 'frontend-processor.py', 'backend-processor.py',
            'debate-processor.py'
        ]
        
        for filename in processor_files:
            file_path = self.script_dir / filename
            if file_path.exists() and not os.access(file_path, os.X_OK):
                try:
                    os.chmod(file_path, 0o755)
                    self.log_fix(f"Made executable: {filename}")
                    repairs_made += 1
                except Exception as e:
                    self.log_warning(f"Could not repair: {filename} - {e}")
        
        # Create logs directory if it doesn't exist
        logs_dir = Path(self.script_dir).parent.parent.parent / "logs"
        if not logs_dir.exists():
            try:
                logs_dir.mkdir(parents=True, exist_ok=True)
                self.log_fix("Created logs directory")
                repairs_made += 1
            except Exception as e:
                self.log_warning(f"Could not create logs directory: {e}")
        
        if repairs_made > 0:
            print(f"\n🎉 Applied {repairs_made} automatic repairs")
            return True
        else:
            print("\n💡 No repairs needed")
            return False
    
    def generate_status_report(self) -> Dict:
        """Generate comprehensive status report"""
        return {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "issues": self.issues,
            "warnings": self.warnings,
            "fixes_applied": self.fixes_applied,
            "status": "healthy" if len(self.issues) == 0 else "issues_detected"
        }
    
    def run_full_check(self, auto_repair: bool = True) -> bool:
        """Run complete health check"""
        print("🏥 Super Prompt Health Check")
        print("=" * 50)
        
        checks = [
            ("Python Environment", self.check_python_environment),
            ("Core Files", self.check_core_files),
            ("Codex CLI", self.check_codex_cli),
            ("Processor Integrity", self.check_processor_integrity),
            ("Cursor Integration", self.check_cursor_integration)
        ]
        
        results = {}
        
        for check_name, check_func in checks:
            results[check_name] = check_func()
        
        if auto_repair and any(not result for result in results.values()):
            self.perform_auto_repair()
        
        # Final summary
        print("\n" + "=" * 50)
        print("📊 HEALTH CHECK SUMMARY")
        print("=" * 50)
        
        for check_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {check_name}")
        
        if self.issues:
            print(f"\n❌ {len(self.issues)} critical issues detected")
            for issue in self.issues:
                print(f"   • {issue}")
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} warnings")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.fixes_applied:
            print(f"\n🔧 {len(self.fixes_applied)} fixes applied")
        
        overall_health = len(self.issues) == 0
        
        if overall_health:
            print("\n🎉 Super Prompt is healthy and ready!")
        else:
            print("\n🚨 Super Prompt requires attention")
            print("   Please resolve critical issues above")
        
        return overall_health

def main():
    """Health check entry point"""
    checker = HealthChecker()
    
    # Command line options
    auto_repair = "--no-repair" not in sys.argv
    
    healthy = checker.run_full_check(auto_repair=auto_repair)
    
    # Save status report
    try:
        import json
        report = checker.generate_status_report()
        report_path = checker.script_dir / "health-report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Health report saved: {report_path}")
    except Exception as e:
        print(f"\n⚠️  Could not save health report: {e}")
    
    return 0 if healthy else 1

if __name__ == "__main__":
    sys.exit(main())