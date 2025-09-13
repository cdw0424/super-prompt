#!/usr/bin/env python3
"""
Frontend Development Processor
Stable subprocess-based execution for frontend development
"""

import sys
from pathlib import Path

# Import stable processor template
sys.path.insert(0, str(Path(__file__).parent))
from processor_template import create_processor

# Create main function using stable template
main = create_processor(
    persona_name="Frontend Development Specialist",
    persona_icon="🎨", 
    description="Expert in user-centered frontend development and UX optimization",
    best_for=[
        "UI/UX design and implementation",
        "Component architecture planning",
        "Performance optimization",
        "Accessibility improvements", 
        "Responsive design challenges"
    ],
    persona_key="frontend"
)

if __name__ == "__main__":
    sys.exit(main(sys.argv))