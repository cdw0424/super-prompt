"""
Context Cache - Cache context collection results
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    content: Any
    timestamp: float
    hits: int = 0
    size_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        return cls(**data)


class ContextCache:
    """
    Cache for context collection results to improve performance
    and reduce redundant processing.
    """

    def __init__(self, cache_dir: Optional[Path] = None, max_size_mb: float = 100.0):
        self.cache_dir = cache_dir or Path(".super-prompt") / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "context_cache.json"
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)  # Convert MB to bytes

        # In-memory cache
        self.memory_cache: Dict[str, CacheEntry] = {}
        self._load_cache()

    # Mapping-style helpers -------------------------------------------------
    def __contains__(self, key: str) -> bool:
        """Support `key in cache` syntax."""
        return key in self.memory_cache

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access while tracking hits."""
        entry = self.memory_cache[key]
        entry.hits += 1
        return entry.content

    def __setitem__(self, key: str, content: Any) -> None:
        """Allow dictionary-style assignment."""
        self.set(key, content)

    def __len__(self) -> int:
        return len(self.memory_cache)

    def get(self, key: str) -> Optional[Any]:
        """Get cached content by key"""
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            entry.hits += 1
            return entry.content

        return None

    def set(self, key: str, content: Any, ttl_seconds: int = 3600) -> None:
        """Set cache entry with optional TTL"""
        # Calculate content size
        content_str = json.dumps(content, default=str)
        size_bytes = len(content_str.encode('utf-8'))

        # Check if we have space
        if self._get_total_size() + size_bytes > self.max_size_bytes:
            self._evict_old_entries(size_bytes)

        # Create cache entry
        entry = CacheEntry(
            key=key,
            content=content,
            timestamp=time.time(),
            hits=0,
            size_bytes=size_bytes
        )

        self.memory_cache[key] = entry
        self._save_cache()

    def invalidate(self, key: str) -> bool:
        """Invalidate a specific cache entry"""
        if key in self.memory_cache:
            del self.memory_cache[key]
            self._save_cache()
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries"""
        self.memory_cache.clear()
        self._save_cache()

    def cleanup_expired(self, max_age_seconds: int = 86400) -> int:
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = []

        for key, entry in self.memory_cache.items():
            if current_time - entry.timestamp > max_age_seconds:
                expired_keys.append(key)

        for key in expired_keys:
            del self.memory_cache[key]

        if expired_keys:
            self._save_cache()

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.memory_cache)
        total_size = sum(entry.size_bytes for entry in self.memory_cache.values())
        total_hits = sum(entry.hits for entry in self.memory_cache.values())

        if total_entries > 0:
            avg_age = sum(time.time() - entry.timestamp for entry in self.memory_cache.values()) / total_entries
            avg_size = total_size / total_entries
        else:
            avg_age = 0
            avg_size = 0

        return {
            "total_entries": total_entries,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_hits": total_hits,
            "average_age_seconds": round(avg_age, 1),
            "average_size_bytes": round(avg_size, 1),
            "cache_hit_ratio": round(total_hits / max(total_entries, 1), 3)
        }

    def _load_cache(self) -> None:
        """Load cache from disk"""
        if not self.cache_file.exists():
            return

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for key, entry_data in data.items():
                self.memory_cache[key] = CacheEntry.from_dict(entry_data)

        except (json.JSONDecodeError, KeyError, TypeError):
            # Invalid cache file, start fresh
            self.memory_cache.clear()

    def _save_cache(self) -> None:
        """Save cache to disk"""
        try:
            data = {key: entry.to_dict() for key, entry in self.memory_cache.items()}

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception:
            # If we can't save, just continue
            pass

    def _get_total_size(self) -> int:
        """Get total cache size in bytes"""
        return sum(entry.size_bytes for entry in self.memory_cache.values())

    def _evict_old_entries(self, needed_bytes: int) -> None:
        """Evict old entries to make space"""
        # Sort by last access time (oldest first)
        entries = sorted(
            self.memory_cache.items(),
            key=lambda x: x[1].timestamp
        )

        freed_bytes = 0
        to_remove = []

        for key, entry in entries:
            to_remove.append(key)
            freed_bytes += entry.size_bytes

            if freed_bytes >= needed_bytes:
                break

        # Remove the entries
        for key in to_remove:
            del self.memory_cache[key]
