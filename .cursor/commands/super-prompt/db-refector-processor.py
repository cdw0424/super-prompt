#!/usr/bin/env python3
"""
Database Refactoring Processor
Direct integration with db_expert_tools.py for database operations
"""

import sys
import os
import subprocess
from pathlib import Path


def show_usage():
    """Display usage information"""
    print("❌ Usage: db-refector-processor.py <action> [args...]")
    print("\n🗄️ Database Refactoring Specialist")
    print("   Expert in database schema design, optimization, and Prisma integration")
    print("\n📋 Available actions:")
    print("   template [--out path]    - Generate Prisma schema template")
    print("   doc [--schema path] [--out path] - Generate database documentation")
    print("   analyze <description>    - Analyze and suggest database improvements")
    print("\n📋 Best for:")
    print("   - Database schema design and optimization")
    print("   - Prisma integration and migration planning")
    print("   - Index and performance optimization")
    print("   - Database refactoring and normalization")


def find_db_tools():
    """Find the db_expert_tools.py script"""
    # Check if db_expert_tools.py exists in current directory
    current_dir = Path(__file__).parent
    db_tools_path = current_dir / "db_expert_tools.py"

    if db_tools_path.exists():
        return str(db_tools_path)

    # Try other possible locations
    possible_paths = [
        Path(__file__).parent.parent.parent
        / ".super-prompt"
        / "utils"
        / "db_expert_tools.py",
        Path.cwd() / ".super-prompt" / "utils" / "db_expert_tools.py",
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    return None


def main(args):
    if len(args) < 2:
        show_usage()
        return 1

    action = args[1]

    # Find db_expert_tools.py
    db_tools_path = find_db_tools()
    if not db_tools_path:
        print("❌ Error: db_expert_tools.py not found")
        print("   Please ensure the database tools are properly installed")
        return 1

    try:
        if action == "template":
            # Generate Prisma schema template
            cmd = [sys.executable, db_tools_path, "template"] + args[2:]
            result = subprocess.run(cmd)
            return result.returncode

        elif action == "doc":
            # Generate database documentation
            cmd = [sys.executable, db_tools_path, "doc"] + args[2:]
            result = subprocess.run(cmd)
            return result.returncode

        elif action == "analyze":
            # Analyze database schema and provide suggestions
            if len(args) < 3:
                print("❌ Error: Please provide a description for analysis")
                print(
                    '   Example: db-refector-processor.py analyze "Review user table schema"'
                )
                return 1

            description = " ".join(args[2:])
            print("🗄️ Database Analysis Request:")
            print(f"   {description}")
            print("\n💡 Suggestions:")
            print("   1. Use 'template' action to generate Prisma schema starter")
            print(
                "   2. Use 'doc' action to generate documentation from existing schema"
            )
            print("   3. Check generated files for index and optimization suggestions")

            return 0

        else:
            print(f"❌ Error: Unknown action '{action}'")
            show_usage()
            return 1

    except FileNotFoundError as e:
        print(f"❌ Error: Required file not found - {e}")
        return 1

    except PermissionError as e:
        print(f"❌ Error: Permission denied - {e}")
        return 1

    except Exception as e:
        print(f"❌ Error: Failed to execute database tools - {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
