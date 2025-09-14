"""
Unit tests for the Context Collector module.
"""

import pytest
from pathlib import Path
from super_prompt.context.collector import ContextCollector


class TestContextCollector:
    """Test cases for the ContextCollector class."""

    def test_initialization(self, temp_project_root):
        """Test that ContextCollector initializes correctly."""
        collector = ContextCollector(str(temp_project_root))
        assert collector.project_root == temp_project_root
        assert collector.cache == {}

    def test_gitignore_loading(self, temp_project_root, sample_gitignore):
        """Test .gitignore pattern loading."""
        collector = ContextCollector(str(temp_project_root))

        # Should have loaded gitignore patterns
        assert collector.gitignore_spec is not None

        # Test pattern matching
        assert collector._is_ignored(temp_project_root / "__pycache__" / "test.pyc")
        assert collector._is_ignored(temp_project_root / "node_modules" / "package.json")
        assert not collector._is_ignored(temp_project_root / "main.py")

    def test_no_gitignore(self, temp_project_root):
        """Test behavior when no .gitignore exists."""
        collector = ContextCollector(str(temp_project_root))
        # No .gitignore in temp directory
        assert collector.gitignore_spec is None

        # Should not ignore any files
        assert not collector._is_ignored(temp_project_root / "__pycache__" / "test.pyc")

    def test_file_content_reading(self, temp_project_root, sample_python_file):
        """Test reading file content."""
        collector = ContextCollector(str(temp_project_root))

        content = collector._read_file_content(sample_python_file)
        assert "Sample Python application" in content
        assert "def main():" in content

    def test_large_file_truncation(self, temp_project_root):
        """Test large file content truncation."""
        collector = ContextCollector(str(temp_project_root))

        # Create a large file
        large_file = temp_project_root / "large.txt"
        large_content = "x" * 100000  # 100KB of content
        large_file.write_text(large_content)

        content = collector._read_file_content(large_file, max_size=50000)  # 50KB limit
        assert len(content) < 100000
        assert "[File truncated due to size]" in content

    def test_keyword_extraction(self, temp_project_root):
        """Test keyword extraction from queries."""
        collector = ContextCollector(str(temp_project_root))

        # Test normal query
        keywords = collector._extract_keywords("Design a user authentication system")
        assert "design" in keywords
        assert "user" in keywords
        assert "authentication" in keywords
        assert "system" in keywords

        # Test stop word filtering
        keywords = collector._extract_keywords("the and or but authentication system")
        assert "the" not in keywords
        assert "and" not in keywords
        assert "authentication" in keywords

        # Test short words filtering
        keywords = collector._extract_keywords("a an authentication system")
        assert "a" not in keywords
        assert "an" not in keywords

    def test_cache_key_generation(self, temp_project_root, sample_python_file):
        """Test cache key generation."""
        collector = ContextCollector(str(temp_project_root))

        key1 = collector._get_cache_key(sample_python_file)
        key2 = collector._get_cache_key(sample_python_file)

        # Same file should generate same key
        assert key1 == key2

        # Key should contain file path
        assert str(sample_python_file) in key1

    def test_content_summarization(self, temp_project_root):
        """Test content summarization for token limits."""
        collector = ContextCollector(str(temp_project_root))

        # Create long content
        long_content = "This is the beginning. " * 1000 + "This is the middle. " * 1000 + "This is the end. " * 1000

        # Summarize to small token limit
        summary = collector._summarize_content(long_content, 100)  # ~400 chars

        assert len(summary) < len(long_content)
        assert "beginning" in summary
        assert "middle" in summary
        assert "end" in summary
        assert "[...content truncated...]" in summary

    def test_file_prioritization(self, temp_project_root, sample_readme, sample_python_file):
        """Test file prioritization logic."""
        collector = ContextCollector(str(temp_project_root))

        files = [sample_readme, sample_python_file]
        prioritized = collector._prioritize_files(files)

        # Should return list of (path, priority) tuples
        assert len(prioritized) == 2
        assert all(isinstance(item, tuple) and len(item) == 2 for item in prioritized)

        # README should have higher priority than Python file
        readme_priority = next(p for f, p in prioritized if f == sample_readme)
        python_priority = next(p for f, p in prioritized if f == sample_python_file)

        assert readme_priority > python_priority

    def test_important_artifacts_detection(self, temp_project_root, sample_readme, sample_package_json):
        """Test detection of important project artifacts."""
        collector = ContextCollector(str(temp_project_root))

        important_files = collector._get_important_artifacts()

        # Should include README and package.json
        important_paths = [str(f) for f in important_files]
        assert any("README.md" in path for path in important_paths)
        assert any("package.json" in path for path in important_paths)

    def test_context_collection_basic(self, temp_project_root, sample_readme):
        """Test basic context collection."""
        collector = ContextCollector(str(temp_project_root))

        result = collector.collect_context("test query", max_tokens=1000)

        assert "query" in result
        assert result["query"] == "test query"
        assert "files" in result
        assert "metadata" in result
        assert "collection_time" in result["metadata"]

    def test_context_collection_with_files(self, temp_project_root, sample_readme, sample_python_file):
        """Test context collection with actual files."""
        collector = ContextCollector(str(temp_project_root))

        result = collector.collect_context("python main function", max_tokens=2000)

        assert len(result["files"]) > 0

        # Should include both files
        file_paths = [f["path"] for f in result["files"]]
        assert any("README.md" in path for path in file_paths)
        assert any("main.py" in path for path in file_paths)

        # Check token counting
        total_tokens = sum(f["tokens"] for f in result["files"])
        assert total_tokens > 0

    def test_cache_functionality(self, temp_project_root, sample_python_file):
        """Test content caching functionality."""
        collector = ContextCollector(str(temp_project_root))

        # First read should cache
        content1 = collector._read_file_content(sample_python_file)
        assert len(collector.cache) == 1

        # Second read should use cache
        content2 = collector._read_file_content(sample_python_file)
        assert content1 == content2
        assert len(collector.cache) == 1

        # Clear cache
        collector.clear_cache()
        assert len(collector.cache) == 0

    def test_stats_reporting(self, temp_project_root):
        """Test statistics reporting."""
        collector = ContextCollector(str(temp_project_root))

        stats = collector.get_stats()

        assert "cache_size" in stats
        assert "gitignore_loaded" in stats
        assert isinstance(stats["cache_size"], int)
        assert isinstance(stats["gitignore_loaded"], bool)

    def test_error_handling(self, temp_project_root):
        """Test error handling for problematic files."""
        collector = ContextCollector(str(temp_project_root))

        # Try to read non-existent file
        content = collector._read_file_content(temp_project_root / "nonexistent.txt")
        assert content == "[Error reading file]"

    @pytest.mark.skipif(not Path("/usr/bin/rg").exists() and not Path("/usr/local/bin/rg").exists(),
                       reason="ripgrep not available")
    def test_relevant_file_search(self, temp_project_root, sample_python_file):
        """Test ripgrep-based relevant file search."""
        collector = ContextCollector(str(temp_project_root))

        # This test requires ripgrep to be installed
        relevant_files = collector._find_relevant_files("main function")

        # Should find the Python file
        assert len(relevant_files) >= 1
        assert sample_python_file in relevant_files
