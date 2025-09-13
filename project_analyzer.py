#!/usr/bin/env python3
"""
Super Prompt Project Analyzer
Direct analysis tool that works independently of the CLI system
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess

class ProjectAnalyzer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.findings = []
        self.recommendations = []

    def analyze_project_structure(self):
        """Analyze the overall project structure"""
        print("🔍 Analyzing project structure...")

        # Check for key directories
        key_dirs = [
            'packages/core-py',
            'packages/cursor-assets',
            '.super-prompt',
            'packages/cli-node',
            'docs',
            'scripts',
            'specs'
        ]

        existing_dirs = []
        missing_dirs = []

        for dir_path in key_dirs:
            if (self.project_root / dir_path).exists():
                existing_dirs.append(dir_path)
            else:
                missing_dirs.append(dir_path)

        if existing_dirs:
            print(f"✅ Found key directories: {', '.join(existing_dirs)}")

        if missing_dirs:
            self.recommendations.append({
                'type': 'structure',
                'priority': 'medium',
                'title': 'Missing standard directories',
                'description': f'Consider adding: {", ".join(missing_dirs)}',
                'action': 'Create standard project structure'
            })

    def analyze_dependencies(self):
        """Analyze Python and Node.js dependencies"""
        print("🔍 Analyzing dependencies...")

        # Check Python dependencies
        if (self.project_root / 'packages/core-py/pyproject.toml').exists():
            print("✅ Python project with pyproject.toml found")
        else:
            self.recommendations.append({
                'type': 'dependency',
                'priority': 'high',
                'title': 'Missing Python dependency management',
                'description': 'Consider adding pyproject.toml for better dependency management',
                'action': 'Create pyproject.toml'
            })

        # Check Node.js dependencies
        if (self.project_root / 'package.json').exists():
            print("✅ Node.js project with package.json found")
        else:
            self.recommendations.append({
                'type': 'dependency',
                'priority': 'high',
                'title': 'Missing Node.js dependency management',
                'description': 'Consider adding package.json for Node.js dependencies',
                'action': 'Create package.json'
            })

    def analyze_code_quality(self):
        """Analyze code quality indicators"""
        print("🔍 Analyzing code quality...")

        # Check for virtual environment
        venv_paths = ['venv', 'env', '.venv']
        venv_found = False
        for venv_path in venv_paths:
            if (self.project_root / venv_path).exists():
                print(f"✅ Virtual environment found: {venv_path}")
                venv_found = True
                break

        if not venv_found:
            self.recommendations.append({
                'type': 'quality',
                'priority': 'high',
                'title': 'No virtual environment detected',
                'description': 'Consider creating a virtual environment for Python dependencies',
                'action': 'python3 -m venv venv && source venv/bin/activate'
            })

        # Check for test directories
        test_found = False
        for root, dirs, files in os.walk(self.project_root):
            if 'test' in root.lower() or 'tests' in root.lower():
                test_found = True
                print(f"✅ Test directory found: {root}")
                break

        if not test_found:
            self.recommendations.append({
                'type': 'quality',
                'priority': 'medium',
                'title': 'No test directories found',
                'description': 'Consider adding unit and integration tests',
                'action': 'Create tests/ directory with appropriate test structure'
            })

    def analyze_configuration(self):
        """Analyze configuration files"""
        print("🔍 Analyzing configuration...")

        # Check for .gitignore
        if not (self.project_root / '.gitignore').exists():
            self.recommendations.append({
                'type': 'config',
                'priority': 'high',
                'title': 'Missing .gitignore',
                'description': 'Consider adding .gitignore to exclude unnecessary files',
                'action': 'Create .gitignore with Python/Node.js patterns'
            })

        # Check for README
        if not (self.project_root / 'README.md').exists():
            self.recommendations.append({
                'type': 'docs',
                'priority': 'high',
                'title': 'Missing README.md',
                'description': 'Consider adding documentation for the project',
                'action': 'Create README.md with project description and setup instructions'
            })

    def analyze_git_status(self):
        """Analyze git status"""
        print("🔍 Analyzing git status...")

        try:
            # Check git status
            result = subprocess.run(['git', 'status', '--porcelain'],
                                  capture_output=True, text=True, cwd=self.project_root)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0]:  # Has changes
                    modified_count = len([l for l in lines if l.startswith(' M')])
                    untracked_count = len([l for l in lines if l.startswith('??')])

                    if modified_count > 0:
                        print(f"⚠️  {modified_count} modified files")
                        self.recommendations.append({
                            'type': 'git',
                            'priority': 'low',
                            'title': 'Uncommitted changes',
                            'description': f'{modified_count} files have been modified but not committed',
                            'action': 'Review and commit changes: git add . && git commit -m "..."'
                        })

                    if untracked_count > 0:
                        print(f"ℹ️  {untracked_count} untracked files")
                        self.recommendations.append({
                            'type': 'git',
                            'priority': 'low',
                            'title': 'Untracked files',
                            'description': f'{untracked_count} files are not tracked by git',
                            'action': 'Add to git: git add <files> or update .gitignore'
                        })
                else:
                    print("✅ Working directory is clean")
            else:
                print("⚠️  Git repository not found or not initialized")
                self.recommendations.append({
                    'type': 'git',
                    'priority': 'medium',
                    'title': 'No git repository',
                    'description': 'Consider initializing git for version control',
                    'action': 'git init && git add . && git commit -m "Initial commit"'
                })

        except Exception as e:
            print(f"⚠️  Could not check git status: {e}")

    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "="*60)
        print("📋 PROJECT ANALYSIS REPORT")
        print("="*60)

        # Summary
        total_recommendations = len(self.recommendations)
        high_priority = len([r for r in self.recommendations if r['priority'] == 'high'])
        medium_priority = len([r for r in self.recommendations if r['priority'] == 'medium'])
        low_priority = len([r for r in self.recommendations if r['priority'] == 'low'])

        print("\n📊 SUMMARY:")
        print(f"   Total recommendations: {total_recommendations}")
        if high_priority > 0:
            print(f"   🔴 High priority: {high_priority}")
        if medium_priority > 0:
            print(f"   🟡 Medium priority: {medium_priority}")
        if low_priority > 0:
            print(f"   🟢 Low priority: {low_priority}")

        # Group recommendations by type
        if self.recommendations:
            print("\n🎯 RECOMMENDATIONS BY CATEGORY:")
            categories = {}
            for rec in self.recommendations:
                cat = rec['type']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(rec)

            for category, recs in categories.items():
                print(f"\n🔧 {category.upper()}:")
                for rec in recs:
                    priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[rec['priority']]
                    print(f"   {priority_icon} {rec['title']}")
                    print(f"      {rec['description']}")
                    print(f"      💡 {rec['action']}")
        else:
            print("\n✅ No major issues found! Project structure looks good.")

        print("\n" + "="*60)
        print("🔍 ANALYSIS COMPLETE")
        print("="*60)

    def run_analysis(self):
        """Run complete project analysis"""
        print("🚀 Starting comprehensive project analysis...")
        print(f"📂 Project: {self.project_root}")

        self.analyze_project_structure()
        self.analyze_dependencies()
        self.analyze_code_quality()
        self.analyze_configuration()
        self.analyze_git_status()

        self.generate_report()

def main():
    # Get project root
    project_root = Path(__file__).resolve().parent

    # Create analyzer and run analysis
    analyzer = ProjectAnalyzer(project_root)
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
