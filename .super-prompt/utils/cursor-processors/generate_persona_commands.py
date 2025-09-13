#!/usr/bin/env python3
"""
Generate Enhanced Persona Commands for Cursor
Based on the enhanced_personas.yaml manifest
"""

import os
import yaml
from pathlib import Path
from jinja2 import Template


def generate_persona_commands():
    """Generate all persona commands from manifest"""

    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    manifest_path = project_root / "packages" / "cursor-assets" / "manifests" / "enhanced_personas.yaml"
    cursor_commands_dir = project_root / ".cursor" / "commands" / "super-prompt"

    # Load manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Command template
    command_template = Template('''#!/usr/bin/env python3
"""
{{ persona_name }} Persona Command
Enhanced based on LLM coding assistant research

Persona Type: {{ role_type }}
Expertise: {{ expertise_level }}
Goal: {{ goal_orientation }}
Style: {{ interaction_style }}
"""

import subprocess
import sys
import os

def main():
    # Use enhanced persona processor
    processor_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                  '.super-prompt', 'utils', 'cursor-processors',
                                  'enhanced_persona_processor.py')

    subprocess.run([
        'python3', processor_path,
        '--persona', '{{ persona_key }}',
        '--user-input', ' '.join(sys.argv[1:]) if sys.argv[1:] else 'Hello! How can I help you today?'
    ], check=False)

if __name__ == "__main__":
    main()
''')

    # Markdown template
    md_template = Template('''# {{ icon }} {{ persona_name }}

**Role**: {{ role_type }} | **Expertise**: {{ expertise_level }}
**Goal Orientation**: {{ goal_orientation }} | **Interaction Style**: {{ interaction_style }}
**Tone**: {{ tone }}

## Persona Definition
{{ persona_definition }}

## Specializations
{% for spec in specializations %}
- {{ spec }}
{% endfor %}

## Auto-Activation Patterns
{% for pattern in auto_activate_patterns %}
- `{{ pattern }}`
{% endfor %}

{% if quality_gates %}
## Quality Gates
{% for gate in quality_gates %}
- {{ gate }}
{% endfor %}
{% endif %}

## Usage
```
/{{ persona_key }} [your request]
```

{% if collaboration_with %}
## Collaboration
Works best with:
{% for other_persona, description in collaboration_with.items() %}
- **{{ other_persona }}**: {{ description }}
{% endfor %}
{% endif %}

---
*Enhanced based on LLM coding assistant research (2022-2025)*
''')

    # Generate commands for each persona
    for persona_key, persona_data in data['personas'].items():
        # Generate Python command file
        command_content = command_template.render(
            persona_name=persona_data['name'],
            persona_key=persona_key,
            role_type=persona_data['role_type'],
            expertise_level=persona_data['expertise_level'],
            goal_orientation=persona_data['goal_orientation'],
            interaction_style=persona_data['interaction_style']
        )

        command_file = cursor_commands_dir / f"{persona_key}.py"
        with open(command_file, 'w', encoding='utf-8') as f:
            f.write(command_content)

        # Make executable
        os.chmod(command_file, 0o755)

        # Generate markdown documentation
        md_content = md_template.render(
            icon=persona_data['icon'],
            persona_name=persona_data['name'],
            persona_key=persona_key,
            role_type=persona_data['role_type'],
            expertise_level=persona_data['expertise_level'],
            goal_orientation=persona_data['goal_orientation'],
            interaction_style=persona_data['interaction_style'],
            tone=persona_data['tone'],
            persona_definition=persona_data['persona_definition'].strip(),
            specializations=persona_data['specializations'],
            auto_activate_patterns=persona_data['auto_activate_patterns'],
            quality_gates=persona_data.get('quality_gates'),
            collaboration_with=persona_data.get('collaboration_with')
        )

        md_file = cursor_commands_dir / f"{persona_key}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"Generated: {persona_key}.py and {persona_key}.md")

    # Generate index file
    index_content = """# 🎭 Enhanced Super Prompt Personas

Based on LLM coding assistant research (2022-2025), implementing:
- Multi-agent role-playing strategies
- Specialized expertise personas
- Adaptive interaction styles
- Goal-oriented behavior patterns

## Available Personas

### 🏗️ Core Development Team
- `/architect` - System architecture and scalability specialist
- `/security` - Security analysis and threat modeling expert
- `/performance` - Performance optimization and bottleneck analysis

### ⚙️ Implementation Team
- `/backend` - Server-side development and API specialist
- `/frontend` - UI/UX and accessibility-focused development

### 🔍 Analysis & Quality
- `/analyzer` - Root cause analysis and systematic investigation
- `/qa` - Comprehensive quality assurance and testing

### 🎓 Knowledge & Guidance
- `/mentor` - Educational guidance and knowledge transfer
- `/refactorer` - Code quality improvement and technical debt reduction

### 🚀 Specialized Roles
- `/devops` - Infrastructure automation and reliability engineering
- `/scribe` - Technical writing and documentation

## Usage
```
/[persona] [your request]
```

## Features
- **Auto-detection**: Personas can auto-activate based on request patterns
- **Multi-persona collaboration**: Complex tasks can trigger multiple persona consultation
- **Adaptive communication**: Each persona adapts tone and style to context
- **Quality gates**: Built-in quality assurance for each persona's domain

---
*For detailed persona specifications, see individual .md files*
"""

    index_file = cursor_commands_dir / "README.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)

    print(f"\nGenerated {len(data['personas'])} personas successfully!")
    print("Generated README.md index file")


if __name__ == "__main__":
    generate_persona_commands()