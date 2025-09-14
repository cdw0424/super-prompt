"""
Tests for the AMR (Auto Model Router) implementation
"""

import pytest
from super_prompt.engine.amr_router import AMRRouter, ComplexityLevel, RouteDecision


class TestAMRRouter:
    """Test cases for AMRRouter class"""

    def test_initialization(self, amr_router: AMRRouter):
        """Test router initialization"""
        assert amr_router is not None
        assert len(amr_router.high_complexity_patterns) > 0
        assert len(amr_router.medium_complexity_patterns) > 0
        assert len(amr_router.low_complexity_patterns) > 0

    def test_high_complexity_detection(self, amr_router: AMRRouter, high_complexity_input: str):
        """Test detection of high complexity tasks"""
        decision = amr_router.analyze_complexity(high_complexity_input)

        assert decision.complexity == ComplexityLevel.H
        assert decision.confidence > 0.6
        assert "ultrathink" in decision.suggested_flags
        assert "security" in decision.reasoning.lower()

    def test_medium_complexity_detection(self, amr_router: AMRRouter, medium_complexity_input: str):
        """Test detection of medium complexity tasks"""
        decision = amr_router.analyze_complexity(medium_complexity_input)

        assert decision.complexity == ComplexityLevel.L1
        assert decision.confidence > 0.4
        assert "implement" in decision.reasoning.lower()

    def test_low_complexity_detection(self, amr_router: AMRRouter, low_complexity_input: str):
        """Test detection of low complexity tasks"""
        decision = amr_router.analyze_complexity(low_complexity_input)

        assert decision.complexity == ComplexityLevel.L0
        assert decision.confidence > 0.3
        assert len(decision.suggested_flags) == 0

    def test_context_influence_on_complexity(self, amr_router: AMRRouter):
        """Test how context affects complexity scoring"""
        simple_input = "Create a function"

        # Test with simple context
        simple_context = {"file_count": 5, "project_size": "small"}
        decision1 = amr_router.analyze_complexity(simple_input, simple_context)

        # Test with complex context
        complex_context = {
            "file_count": 150,
            "project_size": "large",
            "recent_failures": 3,
            "domains": ["frontend", "backend", "database"]
        }
        decision2 = amr_router.analyze_complexity(simple_input, complex_context)

        # Complex context should increase complexity
        assert decision2.complexity.value >= decision1.complexity.value

    def test_pattern_matching_architecture(self, amr_router: AMRRouter):
        """Test architecture-related pattern matching"""
        inputs = [
            "Design a microservices architecture",
            "Refactor the system for better scalability",
            "Architect a new payment processing system"
        ]

        for input_text in inputs:
            decision = amr_router.analyze_complexity(input_text)
            assert decision.complexity == ComplexityLevel.H

    def test_pattern_matching_security(self, amr_router: AMRRouter):
        """Test security-related pattern matching"""
        inputs = [
            "Audit the authentication system for vulnerabilities",
            "Implement OAuth2 security",
            "Check for SQL injection risks"
        ]

        for input_text in inputs:
            decision = amr_router.analyze_complexity(input_text)
            assert decision.complexity == ComplexityLevel.H

    def test_pattern_matching_implementation(self, amr_router: AMRRouter):
        """Test implementation-related pattern matching"""
        inputs = [
            "Create a React component for user profile",
            "Build an API endpoint for data retrieval",
            "Develop a new feature for notifications"
        ]

        for input_text in inputs:
            decision = amr_router.analyze_complexity(input_text)
            assert decision.complexity in [ComplexityLevel.L1, ComplexityLevel.H]

    def test_should_route_high(self, amr_router: AMRRouter):
        """Test quick high-complexity routing check"""
        high_input = "Perform comprehensive security analysis of the entire system"
        low_input = "Show me the current files"

        assert amr_router.should_route_high(high_input) is True
        assert amr_router.should_route_high(low_input) is False

    def test_get_routing_suggestion(self, amr_router: AMRRouter):
        """Test human-readable routing suggestions"""
        high_input = "Optimize performance and identify bottlenecks"
        suggestion = amr_router.get_routing_suggestion(high_input)

        assert "High complexity" in suggestion
        assert "🧠" in suggestion
        assert "confidence:" in suggestion

    def test_confidence_scoring(self, amr_router: AMRRouter):
        """Test confidence scoring consistency"""
        # High complexity input should have high confidence
        high_input = "Architecture review and security audit with performance optimization"
        decision = amr_router.analyze_complexity(high_input)
        assert decision.confidence > 0.7

        # Ambiguous input should have lower confidence
        ambiguous_input = "Do something with the code"
        decision = amr_router.analyze_complexity(ambiguous_input)
        assert decision.confidence < 0.8

    def test_edge_cases(self, amr_router: AMRRouter):
        """Test edge cases and boundary conditions"""
        # Empty input
        decision = amr_router.analyze_complexity("")
        assert decision.complexity is not None

        # Very long input
        long_input = "analyze " * 1000
        decision = amr_router.analyze_complexity(long_input)
        assert decision.complexity == ComplexityLevel.H

        # Mixed signals
        mixed_input = "show me help with architecture design"
        decision = amr_router.analyze_complexity(mixed_input)
        assert decision.complexity is not None

    def test_context_scoring(self, amr_router: AMRRouter):
        """Test context scoring mechanism"""
        # Test large project context
        large_context = {"file_count": 200, "project_size": "large"}
        score = amr_router._analyze_context(large_context)
        assert score >= 1.5

        # Test small project context
        small_context = {"file_count": 3, "project_size": "small"}
        score = amr_router._analyze_context(small_context)
        assert score < 1.0

        # Test failure history context
        failure_context = {"recent_failures": 5}
        score = amr_router._analyze_context(failure_context)
        assert score >= 0.5

    def test_pattern_count_accuracy(self, amr_router: AMRRouter):
        """Test pattern matching count accuracy"""
        text_with_multiple_patterns = "debug the security architecture performance issues"

        high_matches = amr_router._count_pattern_matches(
            text_with_multiple_patterns,
            amr_router.high_complexity_patterns
        )

        # Should match multiple high complexity patterns
        assert high_matches >= 3  # debug, security, architecture, performance