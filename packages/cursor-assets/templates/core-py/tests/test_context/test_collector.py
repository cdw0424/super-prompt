"""
Tests for the context collector implementation
"""

import pytest
import os
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from super_prompt.context.collector import ContextCollector, FileInfo, CollectionResult


class TestContextCollector:
    """Test cases for ContextCollector class"""

    def test_initialization(self, temp_dir: Path):
        """Test collector initialization"""
        collector = ContextCollector(str(temp_dir))

        assert collector.root_path == temp_dir
        assert len(collector.binary_extensions) > 0
        assert '.jpg' in collector.binary_extensions
        assert '.py' not in collector.binary_extensions

    def test_load_gitignore_existing(self, temp_dir: Path):
        """Test loading existing .gitignore file"""
        gitignore_content = """
# Comments should be ignored
node_modules/
*.pyc
dist/
        """.strip()

        (temp_dir / '.gitignore').write_text(gitignore_content)
        collector = ContextCollector(str(temp_dir))

        assert collector.gitignore_spec is not None

    def test_load_gitignore_missing(self, temp_dir: Path):
        """Test behavior when .gitignore is missing"""
        collector = ContextCollector(str(temp_dir))

        # Should handle missing .gitignore gracefully
        assert collector.gitignore_spec is None

    def test_is_binary_file_by_extension(self, temp_dir: Path):
        """Test binary file detection by extension"""
        collector = ContextCollector(str(temp_dir))

        # Create test files
        binary_file = temp_dir / "test.jpg"
        text_file = temp_dir / "test.py"

        binary_file.write_bytes(b"fake image data")
        text_file.write_text("print('hello')")

        assert collector._is_binary_file(binary_file) is True
        assert collector._is_binary_file(text_file) is False

    def test_is_binary_file_by_content(self, temp_dir: Path):
        """Test binary file detection by content"""
        collector = ContextCollector(str(temp_dir))

        # Create file with NULL bytes (binary indicator)
        binary_file = temp_dir / "unknown_binary"
        binary_file.write_bytes(b"text with \x00 null byte")

        assert collector._is_binary_file(binary_file) is True

    @patch('subprocess.run')
    def test_get_git_changed_files_success(self, mock_run, temp_dir: Path):
        """Test successful git changed files detection"""
        # Mock git commands
        mock_run.side_effect = [
            # git diff --name-only
            Mock(returncode=0, stdout="changed_file.py\nmodified.js\n"),
            # git diff --staged --name-only
            Mock(returncode=0, stdout="staged_file.py\n"),
        ]

        collector = ContextCollector(str(temp_dir))
        changed_files = collector._get_git_changed_files()

        expected_files = {"changed_file.py", "modified.js", "staged_file.py"}
        assert changed_files == expected_files

    @patch('subprocess.run')
    def test_get_git_changed_files_failure(self, mock_run, temp_dir: Path):
        """Test git command failure handling"""
        # Mock git command failure
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')

        collector = ContextCollector(str(temp_dir))
        changed_files = collector._get_git_changed_files()

        # Should return empty set on failure
        assert changed_files == set()

    def test_calculate_priority(self, temp_dir: Path):
        """Test file priority calculation"""
        collector = ContextCollector(str(temp_dir))
        git_changed = {"priority_file.py", "changed.js"}

        # Test different file types
        high_priority_file = temp_dir / "priority_file.py"
        config_file = temp_dir / "package.json"
        readme_file = temp_dir / "README.md"
        regular_file = temp_dir / "regular.txt"

        high_priority = collector._calculate_priority(high_priority_file, git_changed)
        config_priority = collector._calculate_priority(config_file, git_changed)
        readme_priority = collector._calculate_priority(readme_file, git_changed)
        regular_priority = collector._calculate_priority(regular_file, git_changed)

        # Recently changed files should have highest priority
        assert high_priority > config_priority
        assert config_priority > readme_priority
        assert readme_priority > regular_priority

    def test_collect_files_basic(self, sample_project: Path):
        """Test basic file collection"""
        collector = ContextCollector(str(sample_project))
        result = collector.collect_files(max_files=10, max_total_size=50000)

        assert isinstance(result, CollectionResult)
        assert len(result.files) > 0
        assert result.total_size > 0
        assert result.collection_time > 0

        # Verify files have content
        for file_info in result.files:
            assert file_info.content is not None
            assert len(file_info.content) > 0

    def test_collect_files_respects_limits(self, sample_project: Path):
        """Test that collection respects file and size limits"""
        collector = ContextCollector(str(sample_project))

        # Very restrictive limits
        result = collector.collect_files(max_files=2, max_total_size=1000)

        assert len(result.files) <= 2
        assert result.total_size <= 1000

    def test_collect_files_excludes_binary(self, sample_project: Path):
        """Test that binary files are excluded"""
        collector = ContextCollector(str(sample_project))
        result = collector.collect_files()

        # Check that binary.bin is not included
        file_paths = [f.path for f in result.files]
        assert "binary.bin" not in file_paths

    def test_collect_files_priority_ordering(self, sample_project: Path):
        """Test that files are ordered by priority"""
        collector = ContextCollector(str(sample_project))

        with patch.object(collector, '_get_git_changed_files', return_value={"README.md"}):
            result = collector.collect_files()

        # README.md should be high priority due to git changes
        if result.files:
            high_priority_files = [f for f in result.files if f.priority > 50]
            assert len(high_priority_files) > 0

    def test_collect_files_with_gitignore(self, temp_dir: Path):
        """Test file collection with .gitignore filtering"""
        # Create .gitignore
        (temp_dir / '.gitignore').write_text("ignored_file.py\nignored_dir/\n")

        # Create files
        (temp_dir / "included_file.py").write_text("# Included")
        (temp_dir / "ignored_file.py").write_text("# Should be ignored")

        ignored_dir = temp_dir / "ignored_dir"
        ignored_dir.mkdir()
        (ignored_dir / "ignored.py").write_text("# In ignored directory")

        collector = ContextCollector(str(temp_dir))
        result = collector.collect_files()

        file_paths = [f.path for f in result.files]
        assert "included_file.py" in file_paths
        assert "ignored_file.py" not in file_paths
        assert "ignored_dir/ignored.py" not in file_paths

    def test_collect_files_error_handling(self, temp_dir: Path):
        """Test error handling during file collection"""
        collector = ContextCollector(str(temp_dir))

        # Create a file, then make it unreadable
        test_file = temp_dir / "unreadable.py"
        test_file.write_text("content")

        # Mock file reading to raise exception
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            result = collector.collect_files()

            # Should handle errors gracefully
            assert isinstance(result, CollectionResult)
            assert result.excluded_count >= 0

    def test_file_info_structure(self, sample_project: Path):
        """Test FileInfo structure and content"""
        collector = ContextCollector(str(sample_project))
        result = collector.collect_files(max_files=1)

        if result.files:
            file_info = result.files[0]

            assert isinstance(file_info, FileInfo)
            assert isinstance(file_info.path, str)
            assert isinstance(file_info.size, int)
            assert isinstance(file_info.modified_time, float)
            assert isinstance(file_info.priority, int)
            assert file_info.content is not None
            assert file_info.size > 0

    def test_large_file_exclusion(self, temp_dir: Path):
        """Test that large files are excluded"""
        collector = ContextCollector(str(temp_dir))

        # Create a large file (over 100KB)
        large_content = "x" * 150000
        large_file = temp_dir / "large_file.txt"
        large_file.write_text(large_content)

        result = collector.collect_files()

        file_paths = [f.path for f in result.files]
        assert "large_file.txt" not in file_paths
        assert result.excluded_count > 0

    def test_collection_performance(self, sample_project: Path):
        """Test that collection completes in reasonable time"""
        collector = ContextCollector(str(sample_project))

        result = collector.collect_files()

        # Collection should complete within 1 second for small projects
        assert result.collection_time < 1.0

    @patch('subprocess.run')
    def test_git_timeout_handling(self, mock_run, temp_dir: Path):
        """Test git command timeout handling"""
        # Mock git command with timeout
        mock_run.side_effect = subprocess.TimeoutExpired('git', 10)

        collector = ContextCollector(str(temp_dir))
        changed_files = collector._get_git_changed_files()

        # Should handle timeout gracefully
        assert changed_files == set()