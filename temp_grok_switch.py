#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/Users/choi-dong-won/Desktop/devs/super-promt/packages/core-py')

from super_prompt.mode_store import set_mode

try:
    result = set_mode('grok')
    print(f"-------- mode: set to {result}")
    print(f"Mode successfully set to: {result}")
except Exception as e:
    print(f"Error setting mode: {e}")
    sys.exit(1)
