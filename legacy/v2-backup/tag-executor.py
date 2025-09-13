#!/usr/bin/env python3
"""
Enhanced Tag Executor - Standalone implementation with AI-powered debate mode
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'templates'))

try:
    # Try to import from the enhanced CLI
    from simple_cli import PromptOptimizer

    def main():
        if len(sys.argv) < 2:
            print("❌ Usage: tag-executor \"your question /tag\"")
            print("\nAvailable Tags:")
            print("- /frontend-ultra: Ultra-detailed frontend development")
            print("- /frontend: Frontend development guidance")
            print("- /backend: Backend development guidance")
            print("- /analyzer: Code analysis and optimization")
            print("- /architect: System architecture design")
            print("- /high: High-level strategic planning")
            print("- /seq: Sequential development planning")
            print("- /seq-ultra: Ultra-detailed sequential planning")
            print("- /debate: Enhanced AI-powered structured debate (10 rounds)")
            print("- /debate-interactive: Interactive step-by-step debate (one round at a time)")
            print("\nExamples:")
            print("  tag-executor \"물렁 복숭아가 맛있을까? /debate\"")
            print("  tag-executor \"토론 주제 /debate-interactive\"")
            return 1

        query = ' '.join(sys.argv[1:])

        try:
            optimizer = PromptOptimizer()
            success = optimizer.process_query(query)
            return 0 if success else 1

        except KeyboardInterrupt:
            print("\n⚠️  Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Tip: Make sure all dependencies are properly installed")
            return 1

    if __name__ == '__main__':
        sys.exit(main())

except ImportError as e:
    # Enhanced fallback with better error handling
    print("❌ Super Prompt modules not found")
    print(f"Import error: {e}")
    print("\n🔧 Troubleshooting steps:")
    print("1. Ensure you're in the correct directory")
    print("2. Check if templates/simple_cli.py exists")
    print("3. Try running: python3 -c \"import sys; sys.path.append('templates'); import simple_cli\"")
    print("4. Or run: npm install (if using npm package)")
    sys.exit(1)
