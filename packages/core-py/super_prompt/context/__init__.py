"""
Context Module - Intelligent file collection and caching

This module provides context-aware file collection with:
- .gitignore respect and binary file exclusion
- Smart caching with file hash indexing
- Token budget management and optimization
- Git-aware priority file detection
"""

from .collector import ContextCollector, FileInfo, CollectionResult
from .cache import FileCache, CacheEntry
from .tokenizer import TokenBudget, TokenCounter

__all__ = [
    "ContextCollector",
    "FileInfo",
    "CollectionResult",
    "FileCache",
    "CacheEntry",
    "TokenBudget",
    "TokenCounter",
]