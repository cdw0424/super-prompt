#!/usr/bin/env python3
"""
Advanced Sequential Thinking Processor (10 Steps)
Stable subprocess-based execution for comprehensive analysis
"""

import sys
from pathlib import Path

# Import stable processor template
sys.path.insert(0, str(Path(__file__).parent))
from processor_template import create_processor

# Create main function using stable template
main = create_processor(
    persona_name="Advanced Sequential Thinking (10 Steps)",
    persona_icon="🧠",
    description="Comprehensive strategic reasoning for enterprise-level complexity",
    best_for=[
        "Enterprise architecture decisions",
        "Complex multi-stakeholder scenarios",
        "Strategic technology planning", 
        "Comprehensive risk assessment",
        "Large-scale system migrations"
    ],
    persona_key="seq-ultra"
)

if __name__ == "__main__":
    sys.exit(main(sys.argv))