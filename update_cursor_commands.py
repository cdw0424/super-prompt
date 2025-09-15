#!/usr/bin/env python3

import os
import re
from pathlib import Path

def update_persona_command(file_path):
    """Update a single persona command file to use MCP"""

    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()

    # Extract persona name from the old run command
    old_pattern = r'args: \["-c", "import subprocess; subprocess.run\(\[\'super-prompt\', \'--persona-([^\']+)\'\].*\]'
    match = re.search(old_pattern, content)

    if not match:
        print(f"Skipping {file_path} - no persona pattern found")
        return False

    persona_name = match.group(1)

    # Replace the YAML frontmatter
    new_frontmatter = f'''---
description: {persona_name} command
run: mcp
tool: sp.{persona_name}
args:
  query: "${{input}}"
---'''

    # Replace everything between the first --- and second ---
    updated_content = re.sub(
        r'^---.*?---',
        new_frontmatter,
        content,
        flags=re.DOTALL | re.MULTILINE
    )

    # Write back to file
    with open(file_path, 'w') as f:
        f.write(updated_content)

    print(f"Updated {file_path} -> sp.{persona_name}")
    return True

def main():
    # Get all command directories that might exist
    search_dirs = [
        "/Users/choi-dong-won/Desktop/devs/super-promt/.cursor/commands/super-prompt",
        "/tmp/test-super-prompt/.cursor/commands/super-prompt"
    ]

    updated_count = 0

    for search_dir in search_dirs:
        if not Path(search_dir).exists():
            print(f"Directory not found: {search_dir}")
            continue

        print(f"Processing directory: {search_dir}")

        # Find all .md files in the directory
        for file_path in Path(search_dir).glob("*.md"):
            if update_persona_command(file_path):
                updated_count += 1

    print(f"\nTotal files updated: {updated_count}")

if __name__ == "__main__":
    main()