"""
Pytest configuration and shared fixtures for Super Prompt tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any

from super_prompt.engine.state_machine import StateMachine
from super_prompt.engine.amr_router import AMRRouter
from super_prompt.context.collector import ContextCollector


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_project(temp_dir: Path) -> Path:
    """Create a sample project structure for testing"""
    # Create basic project structure
    (temp_dir / "src").mkdir()
    (temp_dir / "tests").mkdir()
    (temp_dir / "docs").mkdir()

    # Create some sample files
    (temp_dir / "README.md").write_text("# Sample Project\n\nThis is a test project.")
    (temp_dir / "package.json").write_text('{"name": "test-project", "version": "1.0.0"}')
    (temp_dir / ".gitignore").write_text("node_modules/\n*.pyc\n__pycache__/\n")

    # Source files
    (temp_dir / "src" / "main.py").write_text("""
def main():
    print("Hello, world!")

if __name__ == "__main__":
    main()
""")

    (temp_dir / "src" / "utils.js").write_text("""
function hello() {
    console.log("Hello from JS!");
}

module.exports = { hello };
""")

    # Test files
    (temp_dir / "tests" / "test_main.py").write_text("""
import pytest
from src.main import main

def test_main():
    # Test would go here
    pass
""")

    # Binary file (should be excluded)
    (temp_dir / "binary.bin").write_bytes(b"\x00\x01\x02\x03")

    return temp_dir


@pytest.fixture
def state_machine() -> StateMachine:
    """Create a fresh state machine instance"""
    return StateMachine()


@pytest.fixture
def amr_router() -> AMRRouter:
    """Create an AMR router instance"""
    return AMRRouter()


@pytest.fixture
def context_collector(temp_dir: Path) -> ContextCollector:
    """Create a context collector for the temp directory"""
    return ContextCollector(str(temp_dir))


@pytest.fixture
def sample_context() -> Dict[str, Any]:
    """Sample context data for testing"""
    return {
        "user_input": "Create a new React component",
        "file_count": 25,
        "project_size": "medium",
        "domains": ["frontend", "javascript"],
        "recent_failures": 0
    }


@pytest.fixture
def high_complexity_input() -> str:
    """Sample high complexity input"""
    return "Analyze the security architecture and identify potential vulnerabilities in the authentication system"


@pytest.fixture
def medium_complexity_input() -> str:
    """Sample medium complexity input"""
    return "Implement a new API endpoint for user registration"


@pytest.fixture
def low_complexity_input() -> str:
    """Sample low complexity input"""
    return "Show me the current directory listing"