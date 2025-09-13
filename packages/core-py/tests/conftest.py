"""
Pytest configuration and shared fixtures for Super Prompt tests.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_project_root() -> Generator[Path, None, None]:
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_gitignore(temp_project_root: Path) -> Path:
    """Create a sample .gitignore file."""
    gitignore = temp_project_root / ".gitignore"
    gitignore.write_text("""
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
""")
    return gitignore


@pytest.fixture
def sample_readme(temp_project_root: Path) -> Path:
    """Create a sample README.md file."""
    readme = temp_project_root / "README.md"
    readme.write_text("""# Sample Project

This is a sample project for testing Super Prompt context collection.

## Features

- Feature 1
- Feature 2
- Feature 3

## Usage

```bash
python main.py
```
""")
    return readme


@pytest.fixture
def sample_python_file(temp_project_root: Path) -> Path:
    """Create a sample Python file."""
    py_file = temp_project_root / "main.py"
    py_file.write_text("""
#!/usr/bin/env python3
"""
Sample Python application for testing.
"""

def main():
    print("Hello, World!")
    return "success"

if __name__ == "__main__":
    main()
""")
    return py_file


@pytest.fixture
def sample_package_json(temp_project_root: Path) -> Path:
    """Create a sample package.json file."""
    package_json = temp_project_root / "package.json"
    package_json.write_text("""{
  "name": "sample-project",
  "version": "1.0.0",
  "description": "Sample project for testing",
  "main": "index.js",
  "scripts": {
    "test": "jest",
    "build": "webpack",
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.0",
    "react": "^18.0.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "webpack": "^5.0.0"
  }
}""")
    return package_json


@pytest.fixture
def mock_context_collector(temp_project_root: Path):
    """Create a mock context collector for testing."""
    from super_prompt.context.collector import ContextCollector

    # Initialize with temp directory
    collector = ContextCollector(str(temp_project_root))
    return collector