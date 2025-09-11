#!/usr/bin/env python3
"""
Backend Systems Processor
Stable subprocess-based execution for backend development
"""

import sys
from pathlib import Path

# Import stable processor template
sys.path.insert(0, str(Path(__file__).parent))
from processor_template import create_processor

# Create main function using stable template
main = create_processor(
    persona_name="Backend Systems Specialist",
    persona_icon="⚙️",
    description="Expert in scalable backend development and system optimization", 
    best_for=[
        "API design and implementation",
        "Database architecture and optimization",
        "System scalability planning",
        "Security and authentication",
        "Performance optimization"
    ],
    persona_key="backend"
)

if __name__ == "__main__":
    sys.exit(main(sys.argv))