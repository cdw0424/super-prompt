"""
Unit tests for memory store functionality.

Tests cover:
- Database initialization and persistence
- KV operations (set/get)
- Session and event operations
- Error handling and recovery
- Data persistence across store reopen
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from super_prompt.memory.store import MemoryStore


class TestMemoryStore:
    """Test suite for MemoryStore functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def store(self, temp_dir):
        """Create a memory store instance for testing."""
        return MemoryStore.open(temp_dir)

    def test_store_initialization(self, temp_dir):
        """Test that store initializes correctly and creates database file."""
        store = MemoryStore.open(temp_dir)
        assert store.path.exists()
        assert store.path.name == "context_memory.db"

        # Verify database is accessible
        assert store.path.stat().st_size > 0

    def test_kv_operations(self, store):
        """Test key-value operations."""
        # Test set and get
        store.set_kv("test_key", {"data": "value", "number": 42})
        result = store.get_kv("test_key")
        assert result == {"data": "value", "number": 42}

        # Test non-existent key
        assert store.get_kv("non_existent") is None

        # Test update
        store.set_kv("test_key", "updated_value")
        assert store.get_kv("test_key") == "updated_value"

    def test_session_operations(self, store):
        """Test session creation and event logging."""
        # Create session
        session_id = store.new_session()
        assert isinstance(session_id, int)
        assert session_id > 0

        # Append event
        event_id = store.append_event("test_event", {"action": "test"}, session_id)
        assert isinstance(event_id, int)
        assert event_id > 0

        # Append event without session_id (creates new session)
        event_id2 = store.append_event("test_event2", {"action": "test2"})
        assert isinstance(event_id2, int)

    def test_recent_events(self, store):
        """Test retrieving recent events."""
        # Create some events
        store.append_event("event1", {"data": 1})
        store.append_event("event2", {"data": 2})
        store.append_event("event3", {"data": 3})

        # Get recent events
        events = store.recent_events(10)
        assert len(events) >= 3

        # Check most recent event first
        assert events[0]["type"] == "event3"
        assert events[0]["payload"] == {"data": 3}

    def test_task_tag_helpers(self, store):
        """Test task tag helper methods."""
        # Test setting and getting task tag
        store.set_task_tag("test-task-123")
        assert store.get_task_tag() == "test-task-123"

        # Test None case
        store.set_kv("task_tag", None)
        assert store.get_task_tag() is None

    def test_persistence_across_reopen(self, temp_dir):
        """Test that data persists when store is reopened."""
        # Create store and add data
        store1 = MemoryStore.open(temp_dir)
        store1.set_kv("persistent_key", "persistent_value")
        store1.set_task_tag("persistent-tag")
        session_id = store1.new_session()
        store1.append_event("persistent_event", {"persistent": True}, session_id)

        # Reopen store
        store2 = MemoryStore.open(temp_dir)

        # Verify data persists
        assert store2.get_kv("persistent_key") == "persistent_value"
        assert store2.get_task_tag() == "persistent-tag"

        events = store2.recent_events(10)
        assert len(events) >= 1
        assert events[0]["type"] == "persistent_event"

    def test_error_handling(self, store):
        """Test error handling for various failure scenarios."""
        # Test invalid JSON handling in get_kv (should fallback gracefully)
        import sqlite3
        with sqlite3.connect(str(store.path)) as conn:
            conn.execute("INSERT OR REPLACE INTO kv(key, value, updated_at) VALUES(?, ?, ?)",
                        ("bad_json", "{invalid json", 1234567890))
            conn.commit()

        # Should handle gracefully
        result = store.get_kv("bad_json")
        assert result == "{invalid json"  # Returns raw string

    def test_concurrent_access(self, store):
        """Test concurrent access handling."""
        import threading
        import time

        results = []
        errors = []

        def worker(worker_id):
            try:
                for i in range(10):
                    store.set_kv(f"concurrent_key_{worker_id}_{i}", f"value_{i}")
                    time.sleep(0.001)  # Small delay to encourage contention
                results.append(f"worker_{worker_id}_done")
            except Exception as e:
                errors.append(f"worker_{worker_id}_error: {e}")

        # Start multiple threads
        threads = []
        for i in range(3):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors occurred
        assert len(errors) == 0
        assert len(results) == 3

    def test_database_integrity(self, temp_dir):
        """Test database integrity and schema correctness."""
        store = MemoryStore.open(temp_dir)

        # Verify tables exist
        import sqlite3
        with sqlite3.connect(str(store.path)) as conn:
            cur = conn.cursor()

            # Check tables
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cur.fetchall()}
            assert "kv" in tables
            assert "sessions" in tables
            assert "events" in tables

            # Check indexes
            cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = {row[0] for row in cur.fetchall()}
            assert "idx_sessions_created_at" in indexes
            assert "idx_events_session_ts" in indexes
            assert "idx_events_type_ts" in indexes
