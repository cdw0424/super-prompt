"""
Context Collector - Advanced context collection with ripgrep and caching
"""

import os
import subprocess
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import pathspec
import time

from .tokenizer import Tokenizer
from .cache import ContextCache


class ContextCollector:
    """
    Advanced context collector using ripgrep for fast file scanning
    and intelligent .gitignore processing with caching.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.gitignore_spec = self._load_gitignore()
        self.cache = ContextCache()
        self.tokenizer = Tokenizer()
        self.ripgrep_available = self._check_ripgrep_available()

    def collect_context(self, query: str, max_tokens: int = 16000, use_cache: bool = True) -> Dict[str, any]:
        """
        Collect relevant context for a given query with caching and token optimization.

        Args:
            query: The user's query/request
            max_tokens: Maximum token budget for context
            use_cache: Whether to use caching for performance

        Returns:
            Dictionary containing collected context
        """
        start_time = time.time()

        # Create cache key
        cache_key = self._create_cache_key(query, max_tokens)

        # Check cache first
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                cached_result["metadata"]["cached"] = True
                return cached_result

        # Phase 1: Recent changes (git-based)
        recent_files = self._get_recent_changes()

        # Phase 2: Query-relevant files (ripgrep-based)
        relevant_files = self._find_relevant_files(query)

        # Phase 3: Important artifacts
        important_files = self._get_important_artifacts()

        # Combine and prioritize
        all_files = self._prioritize_files(recent_files + relevant_files + important_files)

        # Extract content with token budgeting
        context_parts = self._extract_content_with_budget(all_files, max_tokens)

        result = {
            "query": query,
            "files": context_parts,
            "metadata": {
                "collection_time": time.time() - start_time,
                "total_files_scanned": len(all_files),
                "context_tokens": sum(self.tokenizer.estimate_tokens(part.get("content", "")) for part in context_parts),
                "ripgrep_used": self.ripgrep_available,
                "cached": False
            }
        }

        # Cache the result
        if use_cache:
            self.cache.set(cache_key, result, ttl_seconds=3600)  # Cache for 1 hour

        return result

    def _load_gitignore(self) -> Optional[pathspec.PathSpec]:
        """Load and parse .gitignore patterns"""
        gitignore_path = self.project_root / ".gitignore"

        if not gitignore_path.exists():
            return None

        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                patterns = f.read().splitlines()

            # Add common ignore patterns
            patterns.extend([
                ".git/",
                "__pycache__/",
                "*.pyc",
                ".DS_Store",
                "node_modules/",
                ".next/",
                "dist/",
                "build/"
            ])

            return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
        except Exception as e:
            print(f"--------context-collector: Failed to load .gitignore: {e}")
            return None

    def _is_ignored(self, path: Path) -> bool:
        """Check if path should be ignored"""
        if not self.gitignore_spec:
            return False

        try:
            relative_path = path.relative_to(self.project_root)
            return self.gitignore_spec.match_file(str(relative_path))
        except ValueError:
            # Path is outside project root
            return True

    def _get_recent_changes(self, days: int = 1) -> List[Path]:
        """Get files changed recently via git"""
        try:
            # Get files modified in last N days
            since = f"{days}.days.ago"
            result = subprocess.run(
                ["git", "log", "--since", since, "--name-only", "--pretty=format:"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                files = set()
                for line in result.stdout.splitlines():
                    line = line.strip()
                    if line and not line.startswith(".git"):
                        file_path = self.project_root / line
                        if file_path.exists() and not self._is_ignored(file_path):
                            files.add(file_path)

                return list(files)

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass

        return []

    def _check_ripgrep_available(self) -> bool:
        """Check if ripgrep is available on the system"""
        return shutil.which("rg") is not None

    def _find_relevant_files(self, query: str, max_files: int = 50) -> List[Path]:
        """Find files relevant to the query using ripgrep or fallback"""
        if not query.strip():
            return []

        # Try ripgrep first if available
        if self.ripgrep_available:
            try:
                return self._find_with_ripgrep(query, max_files)
            except Exception:
                # Fall back to basic search
                pass

        # Fallback: basic file search
        return self._find_with_basic_search(query, max_files)

    def _find_with_ripgrep(self, query: str, max_files: int) -> List[Path]:
        """Find files using ripgrep for fast searching"""
        # Extract keywords from query
        keywords = self._extract_keywords(query)

        if not keywords:
            return []

        # Build ripgrep command with optimizations
        rg_cmd = [
            "rg",
            "--files-with-matches",
            "--smart-case",
            "--hidden",  # Include hidden files
            "--glob", "!{.git,node_modules,__pycache__,.next,.DS_Store}/**"  # Exclude common dirs
        ]
        rg_cmd.extend(keywords[:3])  # Limit to top 3 keywords

        result = subprocess.run(
            rg_cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0:
            files = []
            for line in result.stdout.splitlines():
                file_path = self.project_root / line.strip()
                if file_path.exists() and not self._is_ignored(file_path):
                    files.append(file_path)
                    if len(files) >= max_files:
                        break
            return files

        return []

    def _find_with_basic_search(self, query: str, max_files: int) -> List[Path]:
        """Fallback file search using basic Python methods"""
        keywords = self._extract_keywords(query)
        if not keywords:
            return []

        matching_files = []

        # Walk through project files
        for root, dirs, files in os.walk(self.project_root):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not self._is_ignored(Path(root) / d)]

            for file in files:
                file_path = Path(root) / file

                # Skip ignored files
                if self._is_ignored(file_path):
                    continue

                # Check if file contains keywords
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(10000)  # Read first 10KB

                    content_lower = content.lower()
                    matches = sum(1 for keyword in keywords if keyword in content_lower)

                    if matches > 0:
                        matching_files.append((file_path, matches))
                        if len(matching_files) >= max_files:
                            break

                except Exception:
                    continue

            if len(matching_files) >= max_files:
                break

        # Sort by number of matches and return files
        matching_files.sort(key=lambda x: x[1], reverse=True)
        return [file_path for file_path, _ in matching_files]

    def _create_cache_key(self, query: str, max_tokens: int) -> str:
        """Create a cache key for the query and parameters"""
        key_components = [
            query.strip().lower(),
            str(max_tokens),
            str(self.project_root),
            str(self.ripgrep_available)
        ]
        key_string = "|".join(key_components)
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()

    def _get_important_artifacts(self) -> List[Path]:
        """Get important project artifacts that should always be considered"""
        important_patterns = [
            "README.md",
            "README.rst",
            "package.json",
            "pyproject.toml",
            "requirements.txt",
            "setup.py",
            "Dockerfile",
            "docker-compose.yml",
            "Makefile",
            "specs/**/*.md",
            "docs/**/*.md"
        ]

        important_files = []

        for pattern in important_patterns:
            try:
                if "**" in pattern:
                    # Handle glob patterns
                    import glob
                    matches = glob.glob(str(self.project_root / pattern), recursive=True)
                    for match in matches[:5]:  # Limit per pattern
                        file_path = Path(match)
                        if file_path.exists() and not self._is_ignored(file_path):
                            important_files.append(file_path)
                else:
                    file_path = self.project_root / pattern
                    if file_path.exists() and not self._is_ignored(file_path):
                        important_files.append(file_path)
            except Exception:
                continue

        return important_files

    def _prioritize_files(self, files: List[Path]) -> List[Tuple[Path, int]]:
        """Prioritize files by relevance and recency"""
        prioritized = []

        for file_path in files:
            priority = 1  # Base priority

            # Boost priority for certain file types
            if file_path.name in ["README.md", "package.json", "pyproject.toml"]:
                priority += 10
            elif file_path.suffix in [".md", ".json", ".toml"]:
                priority += 5
            elif file_path.suffix in [".py", ".js", ".ts", ".java", ".go"]:
                priority += 3

            # Boost priority for recently modified files
            try:
                mtime = file_path.stat().st_mtime
                hours_old = (time.time() - mtime) / 3600
                if hours_old < 24:  # Last 24 hours
                    priority += 5
                elif hours_old < 168:  # Last week
                    priority += 2
            except OSError:
                pass

            prioritized.append((file_path, priority))

        # Sort by priority (descending)
        prioritized.sort(key=lambda x: x[1], reverse=True)
        return prioritized

    def _extract_content_with_budget(self, prioritized_files: List[Tuple[Path, int]], max_tokens: int) -> List[Dict]:
        """Extract content from files respecting token budget"""
        context_parts = []
        used_tokens = 0

        for file_path, priority in prioritized_files:
            try:
                # Check cache first
                cache_key = self._get_cache_key(file_path)
                if cache_key in self.cache:
                    content = self.cache[cache_key]
                else:
                    content = self._read_file_content(file_path)
                    self.cache[cache_key] = content

                # Estimate tokens (rough approximation: 1 token ≈ 4 chars)
                content_tokens = len(content) // 4

                if used_tokens + content_tokens <= max_tokens:
                    context_parts.append({
                        "path": str(file_path.relative_to(self.project_root)),
                        "content": content,
                        "priority": priority,
                        "tokens": content_tokens
                    })
                    used_tokens += content_tokens
                else:
                    # Try to fit a summary
                    remaining_tokens = max_tokens - used_tokens
                    if remaining_tokens > 200:  # Minimum useful content
                        summary = self._summarize_content(content, remaining_tokens)
                        summary_tokens = len(summary) // 4

                        context_parts.append({
                            "path": str(file_path.relative_to(self.project_root)),
                            "content": summary,
                            "priority": priority,
                            "tokens": summary_tokens,
                            "truncated": True
                        })
                        used_tokens += summary_tokens

                    break

            except Exception as e:
                print(f"--------context-collector: Error reading {file_path}: {e}")
            continue

        return context_parts

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query"""
        import re

        # Remove common stop words and split
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}
        words = re.findall(r'\b\w+\b', query.lower())

        keywords = []
        for word in words:
            if len(word) > 2 and word not in stop_words:
                keywords.append(word)

        return keywords[:5]  # Limit to top 5

    def _get_cache_key(self, file_path: Path) -> str:
        """Generate cache key for file"""
        try:
            stat = file_path.stat()
            return f"{file_path}:{stat.st_mtime}:{stat.st_size}"
        except OSError:
            return str(file_path)

    def _read_file_content(self, file_path: Path, max_size: int = 102400) -> str:
        """Read file content with size limit"""
        try:
            if file_path.stat().st_size > max_size:
                # For large files, read first part
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(max_size // 2) + "\n\n[File truncated due to size]"

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return "[Error reading file]"

    def _summarize_content(self, content: str, max_tokens: int) -> str:
        """Create a summary of content fitting within token limit"""
        max_chars = max_tokens * 4

        if len(content) <= max_chars:
            return content

        # Simple summarization: take beginning, middle, and end
        part_size = max_chars // 3

        beginning = content[:part_size]
        middle_start = len(content) // 2 - part_size // 2
        middle = content[middle_start:middle_start + part_size]
        end = content[-part_size:]

        return f"{beginning}\n\n[...content truncated...]\n\n{middle}\n\n[...content truncated...]\n\n{end}"

    def clear_cache(self):
        """Clear the content cache"""
        self.cache.clear()

    def get_stats(self) -> Dict[str, any]:
        """Get collector statistics"""
        return {
            "cache_size": len(self.cache),
            "gitignore_loaded": self.gitignore_spec is not None
        }