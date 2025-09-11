#!/usr/bin/env python3
"""
Sequential Thinking Processor (5 Steps)
Stable subprocess-based execution for structured reasoning
"""

import sys
from pathlib import Path

# Import stable processor template
sys.path.insert(0, str(Path(__file__).parent))
from processor_template import create_processor

# Create main function using stable template
main = create_processor(
    persona_name="Sequential Thinking Specialist (5 Steps)",
    persona_icon="🔄",
    description="Structured step-by-step reasoning for complex problems",
    best_for=[
        "Multi-step process design",
        "Complex troubleshooting", 
        "Strategic planning",
        "Logical problem solving",
        "Systematic analysis"
    ],
    persona_key="seq"
)

if __name__ == "__main__":
    sys.exit(main(sys.argv))