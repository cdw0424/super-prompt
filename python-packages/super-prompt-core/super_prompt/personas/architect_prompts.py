# packages/core-py/super_prompt/personas/architect_prompts.py
# Prompt-based architecture analysis and design expert templates
# Always include Mermaid diagrams for visual representation in architecture analysis

from typing import Dict, Any

# GPT mode prompt template
GPT_ARCHITECT_PROMPT = """🏗️ GPT-based System Design Expert

Please analyze the following system design problem:

{query}

## Design Considerations:
1. Architecture pattern evaluation
2. Scalability and maintainability analysis
3. Technology stack optimization suggestions
4. Implementation priority setting

## Required Output Specifications:
**Always include Mermaid diagrams to provide visual architecture representation:**

- System component diagrams (graph TD)
- Data flow diagrams (graph LR)
- Sequence diagrams when needed (sequenceDiagram)
- Deployment diagrams (graph TD)

Please refer to the Cursor Mermaid documentation (https://cursor.com/ko/docs/configuration/tools/mermaid-diagrams) for correct Mermaid syntax.

Provide professional design advice along with **visual diagrams**."""

# Grok mode prompt template
GROK_ARCHITECT_PROMPT = """🏗️ Grok-based System Design Expert

Please analyze the following system design problem creatively:

{query}

## Innovative Design Considerations:
1. Exploration of unique architecture patterns
2. Future-oriented scalability design
3. Utilization of latest technology trends
4. Presentation of innovative solutions

## Required Output Specifications:
**Always include Mermaid diagrams to provide visual architecture representation:**

- Creative system component diagrams (graph TD)
- Innovative data flow diagrams (graph LR)
- Sequence diagrams when needed (sequenceDiagram)
- Future-oriented deployment diagrams (graph TD)

Please refer to the Cursor Mermaid documentation (https://cursor.com/ko/docs/configuration/tools/mermaid-diagrams) for correct Mermaid syntax.

Provide creative and future-oriented design advice along with **visual diagrams**."""

def get_architect_prompt(mode: str, query: str) -> str:
    """Return architecture prompt based on mode"""
    if mode == "grok":
        return GROK_ARCHITECT_PROMPT.format(query=query)
    else:
        return GPT_ARCHITECT_PROMPT.format(query=query)

def get_architect_workflow(mode: str = "gpt") -> Dict[str, Any]:
    """Configure architecture workflow (always includes Mermaid diagrams)"""
    return {
        "persona": "architect",
        "mode": mode,
        "steps": [
            {
                "name": "architecture_analysis",
                "description": "System architecture analysis and Mermaid diagram generation",
                "prompt_template": get_architect_prompt(mode, "{query}")
            },
            {
                "name": "visual_diagrams",
                "description": "Mermaid diagram validation and additional diagram generation",
                "prompt_template": """Please review the generated Mermaid diagrams and create additional diagrams if needed.

Use correct Mermaid syntax according to the Cursor Mermaid documentation (https://cursor.com/ko/docs/configuration/tools/mermaid-diagrams).

Additional diagram types:
- sequenceDiagram: Component interactions
- classDiagram: Class relationships
- stateDiagram-v2: State machines
- erDiagram: Data models"""
            },
            {
                "name": "design_recommendations",
                "description": "Design recommendations and diagram-based optimization",
                "prompt_template": "Please provide specific design improvement suggestions based on the generated diagrams."
            }
        ]
    }
