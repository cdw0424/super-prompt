"""
Performance tests for Super Prompt v3 components
"""

import pytest
import time
from pathlib import Path
from unittest.mock import patch

from super_prompt.engine.state_machine import StateMachine, State
from super_prompt.engine.amr_router import AMRRouter
from super_prompt.context.collector import ContextCollector


class TestPerformance:
    """Performance benchmarks and tests"""

    def test_amr_router_performance(self):
        """Test AMR router response time"""
        amr_router = AMRRouter()

        # Test various input sizes
        test_inputs = [
            "Simple task",
            "This is a medium complexity task with more details about implementation",
            "This is a very long and complex task description that includes multiple domains like architecture design, security analysis, performance optimization, database schema migrations, frontend component development, backend API creation, testing strategies, deployment pipelines, monitoring setup, and comprehensive documentation that spans across different technologies and requires deep technical expertise and system thinking capabilities" * 5
        ]

        for input_text in test_inputs:
            start_time = time.time()
            decision = amr_router.analyze_complexity(input_text)
            end_time = time.time()

            # Should complete within 100ms regardless of input size
            assert (end_time - start_time) < 0.1
            assert decision is not None

    def test_context_collector_performance(self, sample_project: Path):
        """Test context collector performance"""
        collector = ContextCollector(str(sample_project))

        # Test different collection sizes
        collection_sizes = [5, 10, 20, 50]

        for max_files in collection_sizes:
            start_time = time.time()
            result = collector.collect_files(max_files=max_files)
            end_time = time.time()

            # Should complete within reasonable time
            collection_time = end_time - start_time
            assert collection_time < 1.0  # 1 second max

            # Should respect limits
            assert len(result.files) <= max_files

    def test_state_machine_performance(self):
        """Test state machine execution performance"""
        state_machine = StateMachine()

        # Set up lightweight handlers
        def fast_handler(context):
            return {"processed": True}

        # Register handlers for all states
        for state in [State.INTENT, State.CLASSIFY, State.PLAN, State.EXECUTE, State.VERIFY, State.REPORT]:
            state_machine.register_handler(state, fast_handler)

        # Measure execution time
        start_time = time.time()
        result = state_machine.run()
        end_time = time.time()

        # Should complete very quickly with simple handlers
        execution_time = end_time - start_time
        assert execution_time < 0.1  # 100ms max
        assert result.success is True

    def test_large_project_simulation(self, temp_dir: Path):
        """Test performance with simulated large project"""
        # Create a larger project structure
        for i in range(50):
            file_path = temp_dir / f"file_{i}.py"
            file_path.write_text(f"# File {i}\nprint('hello from file {i}')\n" * 10)

        # Create subdirectories
        for i in range(10):
            subdir = temp_dir / f"subdir_{i}"
            subdir.mkdir()
            for j in range(5):
                (subdir / f"subfile_{j}.py").write_text(f"# Subfile {i}_{j}\n")

        collector = ContextCollector(str(temp_dir))

        start_time = time.time()
        result = collector.collect_files(max_files=30)
        end_time = time.time()

        # Should handle larger projects efficiently
        collection_time = end_time - start_time
        assert collection_time < 2.0  # 2 seconds max for larger project
        assert len(result.files) > 0

    def test_memory_usage_context_collection(self, sample_project: Path):
        """Test memory usage during context collection"""
        import tracemalloc

        collector = ContextCollector(str(sample_project))

        tracemalloc.start()

        # Collect files multiple times
        for _ in range(10):
            result = collector.collect_files(max_files=10)
            assert len(result.files) > 0

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Memory usage should be reasonable (less than 10MB peak)
        assert peak < 10 * 1024 * 1024

    def test_concurrent_amr_analysis(self):
        """Test AMR router under concurrent load"""
        import threading
        import queue

        amr_router = AMRRouter()
        results_queue = queue.Queue()

        def analyze_task(input_text):
            try:
                start = time.time()
                decision = amr_router.analyze_complexity(input_text)
                end = time.time()
                results_queue.put((decision, end - start))
            except Exception as e:
                results_queue.put((None, str(e)))

        # Create multiple threads
        threads = []
        inputs = [
            "Create a function",
            "Design a microservices architecture",
            "Fix a bug in the authentication system",
            "Optimize database queries",
            "Write unit tests"
        ] * 4  # 20 concurrent requests

        for input_text in inputs:
            thread = threading.Thread(target=analyze_task, args=(input_text,))
            threads.append(thread)

        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        end_time = time.time()

        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        # All requests should complete successfully
        assert len(results) == len(inputs)

        # No errors
        errors = [r for r in results if isinstance(r[1], str)]
        assert len(errors) == 0

        # Individual response times should be fast
        response_times = [r[1] for r in results if isinstance(r[1], float)]
        max_response_time = max(response_times)
        assert max_response_time < 0.2  # 200ms max per request

        # Total time should be reasonable
        total_time = end_time - start_time
        assert total_time < 2.0  # Should handle 20 concurrent requests in under 2 seconds

    @pytest.mark.parametrize("file_count", [10, 50, 100])
    def test_scalability_context_collection(self, temp_dir: Path, file_count: int):
        """Test context collection scalability with different project sizes"""
        # Create files
        for i in range(file_count):
            file_path = temp_dir / f"test_file_{i}.py"
            content = f"# Test file {i}\n" + "print('test')\n" * (i % 10 + 1)
            file_path.write_text(content)

        collector = ContextCollector(str(temp_dir))

        start_time = time.time()
        result = collector.collect_files(max_files=min(file_count, 50))
        end_time = time.time()

        collection_time = end_time - start_time

        # Time should scale reasonably with project size
        if file_count <= 10:
            assert collection_time < 0.5
        elif file_count <= 50:
            assert collection_time < 1.0
        else:
            assert collection_time < 2.0

        # Should collect files successfully
        assert len(result.files) > 0
        assert result.total_size > 0

    def test_gitignore_performance_large_project(self, temp_dir: Path):
        """Test .gitignore processing performance with large ignore lists"""
        # Create a large .gitignore file
        gitignore_patterns = []
        for i in range(1000):
            gitignore_patterns.append(f"ignore_pattern_{i}")
            gitignore_patterns.append(f"*.ignore_{i}")

        (temp_dir / '.gitignore').write_text('\n'.join(gitignore_patterns))

        # Create many files
        for i in range(100):
            (temp_dir / f"file_{i}.py").write_text(f"content {i}")
            (temp_dir / f"ignore_pattern_{i}").write_text("ignored content")

        collector = ContextCollector(str(temp_dir))

        start_time = time.time()
        result = collector.collect_files()
        end_time = time.time()

        # Should handle large .gitignore efficiently
        collection_time = end_time - start_time
        assert collection_time < 3.0  # Even with complex .gitignore, should be under 3s

        # Should properly exclude ignored files
        file_paths = [f.path for f in result.files]
        ignored_files = [path for path in file_paths if "ignore_pattern_" in path]
        assert len(ignored_files) == 0  # All should be filtered out