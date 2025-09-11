#!/usr/bin/env python3
"""
Deep Reasoning Processor
Stable subprocess-based execution for strategic analysis
"""

import sys
from pathlib import Path

# Import stable processor template
sys.path.insert(0, str(Path(__file__).parent))
from processor_template import create_processor

# Create main function using stable template
main = create_processor(
    persona_name="Deep Reasoning Specialist",
    persona_icon="🧠",
    description="Expert in strategic thinking and complex problem decomposition",
    best_for=[
        "Complex strategic decisions",
        "Multi-faceted problem analysis",
        "Trade-off evaluations", 
        "Long-term impact assessment",
        "Risk evaluation and mitigation"
    ],
    persona_key="high"
)

if __name__ == "__main__":
    sys.exit(main(sys.argv))