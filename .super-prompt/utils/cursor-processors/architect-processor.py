#!/usr/bin/env python3
"""
Systems Architecture Processor
Stable subprocess-based execution for architectural design
"""

import sys
from pathlib import Path

# Import stable processor template
sys.path.insert(0, str(Path(__file__).parent))
from processor_template import create_processor

# Create main function using stable template
main = create_processor(
    persona_name="Systems Architecture Specialist",
    persona_icon="🏗️",
    description="Expert in strategic system design and technical architecture",
    best_for=[
        "System architecture design",
        "Technical strategy planning",
        "Scalability and performance planning",
        "Technology migration strategies",
        "Design pattern recommendations"
    ],
    persona_key="architect"
)

if __name__ == "__main__":
    sys.exit(main(sys.argv))