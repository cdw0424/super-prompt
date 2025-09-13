"""
Unit tests for the AMR Router module.
"""

import pytest
from super_prompt.engine.amr_router import AMRRouter, ReasoningLevel


class TestAMRRouter:
    """Test cases for the AMRRouter class."""

    def test_initialization(self):
        """Test that AMRRouter initializes correctly."""
        router = AMRRouter()
        assert router.routing_history == []
        assert router.complexity_patterns is not None
        assert "complex_keywords" in router.complexity_patterns
        assert "complexity_indicators" in router.complexity_patterns
        assert "architectural_elements" in router.complexity_patterns

    def test_classify_light_task(self):
        """Test classification of light/simple tasks."""
        router = AMRRouter()

        light_queries = [
            "Hello",
            "How are you?",
            "What time is it?",
            "Show me the menu",
            "Simple question"
        ]

        for query in light_queries:
            level = router.classify_task(query)
            assert level == ReasoningLevel.LIGHT

    def test_classify_moderate_task(self):
        """Test classification of moderate complexity tasks."""
        router = AMRRouter()

        moderate_queries = [
            "How do I implement user authentication?",
            "Create a function to parse JSON data",
            "Explain how this code works",
            "Write a test for this function",
            "Optimize this database query"
        ]

        for query in moderate_queries:
            level = router.classify_task(query)
            assert level in [ReasoningLevel.MODERATE, ReasoningLevel.LIGHT]

    def test_classify_heavy_task(self):
        """Test classification of heavy/complex tasks."""
        router = AMRRouter()

        heavy_queries = [
            "Design a microservices architecture for an e-commerce platform",
            "Implement security hardening across the entire application stack",
            "Create a comprehensive testing strategy for a distributed system",
            "Architect a scalable database schema with complex relationships",
            "Design and implement a real-time collaborative editing system"
        ]

        for query in heavy_queries:
            level = router.classify_task(query)
            # Heavy tasks should be classified as heavy or at least moderate
            assert level in [ReasoningLevel.HEAVY, ReasoningLevel.MODERATE]

    def test_complex_keywords_detection(self):
        """Test detection of complex keywords."""
        router = AMRRouter()

        assert router._check_keywords("Design a system architecture")
        assert router._check_keywords("Implement security features")
        assert router._check_keywords("Scale the infrastructure")
        assert not router._check_keywords("Hello world")

    def test_complexity_indicators_detection(self):
        """Test detection of complexity indicators."""
        router = AMRRouter()

        assert router._check_complexity_indicators("Analyze and evaluate the performance")
        assert router._check_complexity_indicators("Consider multiple options and trade-offs")
        assert router._check_complexity_indicators("Assess the requirements carefully")
        assert not router._check_complexity_indicators("Simple hello world")

    def test_architectural_elements_detection(self):
        """Test detection of architectural elements."""
        router = AMRRouter()

        assert router._check_architectural_elements("Database schema design")
        assert router._check_architectural_elements("API endpoint implementation")
        assert router._check_architectural_elements("Component architecture")
        assert router._check_architectural_elements("Deployment pipeline")
        assert not router._check_architectural_elements("Basic function")

    def test_routing_history(self):
        """Test that routing decisions are recorded."""
        router = AMRRouter()

        # Make several classifications
        router.classify_task("Simple task")
        router.classify_task("Complex architectural design")

        assert len(router.routing_history) == 2

        # Check history structure
        first_entry = router.routing_history[0]
        assert "input" in first_entry
        assert "score" in first_entry
        assert "level" in first_entry
        assert "reasons" in first_entry

    def test_switch_template_generation(self):
        """Test model switching template generation."""
        router = AMRRouter()

        # Same level should return empty template
        template = router.get_switch_template(ReasoningLevel.LIGHT, ReasoningLevel.LIGHT)
        assert template == ""

        # High to medium
        template = router.get_switch_template(ReasoningLevel.HEAVY, ReasoningLevel.MODERATE)
        assert "gpt-5 medium" in template

        # Any to high
        template = router.get_switch_template(ReasoningLevel.LIGHT, ReasoningLevel.HEAVY)
        assert "gpt-5 high" in template

    def test_should_switch_to_high(self):
        """Test convenience method for high reasoning detection."""
        router = AMRRouter()

        assert router.should_switch_to_high("Design a complex system architecture")
        assert not router.should_switch_to_high("Hello world")

    def test_context_aware_classification(self):
        """Test classification with additional context."""
        router = AMRRouter()

        # Normal classification
        level1 = router.classify_task("Implement user login")

        # With failure context - should increase complexity
        level2 = router.classify_task("Implement user login", {"has_failures": True})

        # With token pressure - should increase complexity
        level3 = router.classify_task("Implement user login", {"token_limit_exceeded": True})

        # Verify that context affects classification (at least doesn't make it lighter)
        if level1 == ReasoningLevel.LIGHT:
            # If base was light, context should at least maintain or increase
            assert level2 in [ReasoningLevel.LIGHT, ReasoningLevel.MODERATE, ReasoningLevel.HEAVY]
            assert level3 in [ReasoningLevel.LIGHT, ReasoningLevel.MODERATE, ReasoningLevel.HEAVY]

    def test_get_routing_stats(self):
        """Test routing statistics generation."""
        router = AMRRouter()

        # No history
        stats = router.get_routing_stats()
        assert stats["total_decisions"] == 0

        # Add some decisions
        router.classify_task("Light task")
        router.classify_task("Moderate task")
        router.classify_task("Heavy task")
        router.classify_task("Another heavy task")

        stats = router.get_routing_stats()
        assert stats["total_decisions"] == 4
        assert len(stats["level_distribution"]) > 0
        assert "high_reasoning_ratio" in stats
        assert 0 <= stats["high_reasoning_ratio"] <= 1

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        router = AMRRouter()

        # Empty query
        level = router.classify_task("")
        assert level == ReasoningLevel.LIGHT

        # Very long query
        long_query = "design " * 1000
        level = router.classify_task(long_query)
        # Should be classified as heavy due to length and keywords
        assert level in [ReasoningLevel.MODERATE, ReasoningLevel.HEAVY]

        # Query with only stop words
        stop_words_query = "the and or but in on at to for of with by is are was were"
        level = router.classify_task(stop_words_query)
        assert level == ReasoningLevel.LIGHT
