#!/usr/bin/env python3
"""
Simple Tag Executor - Standalone implementation
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import from the CLI
    from simple_cli import PromptOptimizer
    
    def main():
        if len(sys.argv) < 2:
            print("❌ Usage: tag-executor \"your question /tag\"")
            print("\nAvailable Tags: /frontend-ultra, /frontend, /backend, /analyzer, /architect, /high, /seq, /seq-ultra")
            return 1
        
        query = ' '.join(sys.argv[1:])
        
        try:
            optimizer = PromptOptimizer()
            success = optimizer.process_query(query)
            return 0 if success else 1
            
        except KeyboardInterrupt:
            print("\n⚠️  Operation cancelled")
            return 1
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    if __name__ == '__main__':
        sys.exit(main())

except ImportError:
    # Fallback minimal implementation
    print("❌ Super Prompt modules not found")
    print("Please run 'npm install' to complete installation")
    sys.exit(1)