#!/usr/bin/env python3
"""
Root Cause Analysis Processor
Stable subprocess-based execution for systematic troubleshooting
"""

import sys
from pathlib import Path

# Import stable processor template
sys.path.insert(0, str(Path(__file__).parent))
from processor_template import create_processor

# Create main function using stable template
main = create_processor(
    persona_name="Root Cause Analysis Specialist", 
    persona_icon="🔍",
    description="Expert in systematic troubleshooting and diagnostics",
    best_for=[
        "Bug investigation and debugging",
        "Performance issue analysis", 
        "System failure diagnosis",
        "Error pattern analysis",
        "Production incident investigation"
    ],
    persona_key="analyzer"
)

if __name__ == "__main__":
    sys.exit(main(sys.argv))