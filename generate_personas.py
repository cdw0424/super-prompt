#!/usr/bin/env python3
"""
Generate Cursor persona commands from manifest.yaml
"""

import yaml
import os
from pathlib import Path

def generate_persona_commands():
    # Load personas manifest (prefer package asset; fallback to project copy)
    candidates = [
        Path("packages/cursor-assets/manifests/personas.yaml"),
        Path("personas/manifest.yaml"),
    ]
    manifest_path = next((p for p in candidates if p.exists()), None)
    if not manifest_path:
        print("❌ personas manifest not found (looked in packages/cursor-assets/manifests/personas.yaml and personas/manifest.yaml)")
        return

    with open(manifest_path, 'r') as f:
        data = yaml.safe_load(f)

    personas = data.get('personas', {})

    # Ensure output directory exists
    commands_dir = Path(".cursor/commands/super-prompt")
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Generate command files for each persona
    for persona_key, persona_data in personas.items():
        name = persona_data.get('name', persona_key)
        icon = persona_data.get('icon', '🤖')
        description = persona_data.get('description', 'AI Assistant')

        # Special handling for mode commands
        if 'mode-on' in persona_key or 'mode-off' in persona_key:
            if persona_key == 'grok-mode-on':
                command = 'grok-mode-on'
            elif persona_key == 'grok-mode-off':
                command = 'grok-mode-off'
            elif persona_key == 'gpt-mode-on':
                command = 'codex-mode-on'  # Keep internal command name
            elif persona_key == 'gpt-mode-off':
                command = 'codex-mode-off'  # Keep internal command name
            else:
                command = persona_key

            command_content = f"""---
description: {persona_key} command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '{command}'], check=False)"]
---

{icon} {name}
{description}
"""
        else:
            # Regular persona command
            command_content = f"""---
description: {persona_key} command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-{persona_key}'] + __import__('sys').argv[1:], input='${{input}}', text=True, check=False)"]
---

{icon} {name}
{description}
"""

        command_file = commands_dir / f"{persona_key}.md"
        with open(command_file, 'w') as f:
            f.write(command_content)

        print(f"✅ Generated {command_file}")

    print(f"\n🎉 Generated {len(personas)} persona commands in {commands_dir}")

if __name__ == "__main__":
    generate_persona_commands()
