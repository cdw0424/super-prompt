#!/usr/bin/env python3
"""
Simple Persona Command Generator
Without external dependencies
"""

import os
from pathlib import Path


def create_persona_command(persona_key, persona_name, icon, description):
    """Create a persona command file"""

    command_content = f'''#!/usr/bin/env python3
"""
{persona_name} Persona Command
Enhanced based on LLM coding assistant research
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
        '--persona', '{persona_key}',
        '--user-input', ' '.join(sys.argv[1:]) if sys.argv[1:] else 'Hello! How can I help you today?'
    ], check=False)

if __name__ == "__main__":
    main()
'''

    md_content = f'''# {icon} {persona_name}

{description}

## Usage
```
/{persona_key} [your request]
```

---
*Enhanced based on LLM coding assistant research (2022-2025)*
'''

    return command_content, md_content


def main():
    """Generate all persona commands"""

    # Target directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    cursor_commands_dir = project_root / ".cursor" / "commands" / "super-prompt"

    # Ensure directory exists
    cursor_commands_dir.mkdir(parents=True, exist_ok=True)

    # Define personas based on enhanced_personas.yaml
    personas = {
        "architect": {
            "name": "System Architect",
            "icon": "🏗️",
            "description": "Senior System Architect specializing in large-scale distributed systems, microservices, and cloud-native patterns."
        },
        "security": {
            "name": "Security Specialist",
            "icon": "🛡️",
            "description": "Senior Security Engineer and Threat Modeling Expert with expertise in application security and compliance."
        },
        "performance": {
            "name": "Performance Engineer",
            "icon": "⚡",
            "description": "Senior Performance Engineer specializing in optimization, profiling, and scalability engineering."
        },
        "backend": {
            "name": "Backend Engineer",
            "icon": "⚙️",
            "description": "Senior Backend Engineer with expertise in distributed systems, APIs, databases, and cloud infrastructure."
        },
        "frontend": {
            "name": "Frontend Engineer",
            "icon": "🎨",
            "description": "Senior Frontend Engineer specializing in modern web development, accessibility, and user experience."
        },
        "analyzer": {
            "name": "Technical Analyst",
            "icon": "🔍",
            "description": "Senior Technical Analyst specializing in root cause analysis, system debugging, and investigative problem-solving."
        },
        "qa": {
            "name": "Quality Engineer",
            "icon": "✅",
            "description": "Senior Quality Engineer focused on comprehensive quality assurance, test automation, and quality-driven development."
        },
        "mentor": {
            "name": "Senior Mentor",
            "icon": "🎓",
            "description": "Senior Engineering Mentor with extensive teaching experience, focused on knowledge transfer and skill development."
        },
        "refactorer": {
            "name": "Code Quality Specialist",
            "icon": "🔧",
            "description": "Code Quality Specialist focused on improving maintainability, readability, and reducing technical debt."
        },
        "devops": {
            "name": "DevOps Engineer",
            "icon": "🚀",
            "description": "Senior DevOps Engineer specializing in CI/CD, infrastructure automation, monitoring, and site reliability."
        },
        "scribe": {
            "name": "Technical Writer",
            "icon": "📝",
            "description": "Senior Technical Writer specializing in developer documentation, API documentation, and technical communication."
        }
    }

    # Generate commands for each persona
    for persona_key, persona_info in personas.items():
        command_content, md_content = create_persona_command(
            persona_key,
            persona_info["name"],
            persona_info["icon"],
            persona_info["description"]
        )

        # Write command file
        command_file = cursor_commands_dir / f"{persona_key}.py"
        with open(command_file, 'w', encoding='utf-8') as f:
            f.write(command_content)

        # Make executable
        os.chmod(command_file, 0o755)

        # Write markdown file
        md_file = cursor_commands_dir / f"{persona_key}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"Generated: {persona_key}.py and {persona_key}.md")

    # Generate README
    readme_content = """# 🎭 Enhanced Super Prompt Personas

Based on LLM coding assistant research (2022-2025), implementing multi-agent role-playing strategies and specialized expertise.

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
- **Research-Based**: Built on 2022-2025 LLM coding assistant research
- **Role Specialization**: Each persona has specific expertise and communication style
- **Quality Gates**: Built-in quality assurance for each domain
- **Auto-Detection**: Personas can auto-activate based on request patterns

---
*Enhanced personas implementing multi-agent collaboration and specialized expertise patterns*
"""

    readme_file = cursor_commands_dir / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"\nGenerated {len(personas)} personas successfully!")
    print("Generated README.md index file")

    # Clean up old markdown files that don't match our personas
    for file in cursor_commands_dir.glob("*.md"):
        if file.stem not in personas and file.name != "README.md":
            print(f"Cleaning up old file: {file.name}")
            file.unlink()


if __name__ == "__main__":
    main()