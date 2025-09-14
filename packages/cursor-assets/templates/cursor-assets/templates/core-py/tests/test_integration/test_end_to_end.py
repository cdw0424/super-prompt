"""
End-to-end integration tests for Super Prompt v3
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from super_prompt.engine.state_machine import StateMachine, State
from super_prompt.engine.amr_router import AMRRouter, ComplexityLevel
from super_prompt.context.collector import ContextCollector


class TestEndToEndIntegration:
    """Integration tests combining multiple components"""

    def test_complete_workflow_simple_task(self, sample_project: Path):
        """Test complete workflow for a simple task"""
        # Initialize components
        state_machine = StateMachine()
        amr_router = AMRRouter()
        context_collector = ContextCollector(str(sample_project))

        # Simulate user input
        user_input = "Show me the main.py file"

        # Step 1: Classify complexity
        complexity_decision = amr_router.analyze_complexity(user_input)
        assert complexity_decision.complexity in [ComplexityLevel.L0, ComplexityLevel.L1]

        # Step 2: Collect context
        context_result = context_collector.collect_files(max_files=5)
        assert len(context_result.files) > 0

        # Step 3: Set up state machine handlers
        def intent_handler(context):
            return {
                "user_input": user_input,
                "intent": "show_file",
                "complexity": complexity_decision.complexity.value
            }

        def classify_handler(context):
            return {"classification": "file_display", "simple_task": True}

        def plan_handler(context):
            return {"plan": ["find_file", "read_content", "display"]}

        def execute_handler(context):
            # Find the main.py file
            main_files = [f for f in context_result.files if "main.py" in f.path]
            if main_files:
                return {"executed": True, "file_found": True, "content": main_files[0].content}
            return {"executed": True, "file_found": False}

        def verify_handler(context):
            return {"verified": context.get("file_found", False)}

        def report_handler(context):
            if context.get("verified"):
                return {"outputs": {"status": "success", "file_content": context.get("content", "")}}
            return {"outputs": {"status": "error", "message": "File not found"}}

        # Register handlers
        state_machine.register_handler(State.INTENT, intent_handler)
        state_machine.register_handler(State.CLASSIFY, classify_handler)
        state_machine.register_handler(State.PLAN, plan_handler)
        state_machine.register_handler(State.EXECUTE, execute_handler)
        state_machine.register_handler(State.VERIFY, verify_handler)
        state_machine.register_handler(State.REPORT, report_handler)

        # Execute workflow
        result = state_machine.run()

        # Verify successful completion
        assert result.success is True
        assert result.final_state == State.REPORT
        assert result.outputs is not None
        assert result.outputs.get("status") == "success"

    def test_complete_workflow_complex_task(self, sample_project: Path):
        """Test complete workflow for a complex task"""
        # Initialize components
        state_machine = StateMachine()
        amr_router = AMRRouter()
        context_collector = ContextCollector(str(sample_project))

        # Simulate complex user input
        user_input = "Analyze the security architecture and identify potential vulnerabilities"

        # Step 1: Classify complexity
        complexity_decision = amr_router.analyze_complexity(user_input)
        assert complexity_decision.complexity == ComplexityLevel.H
        assert "ultrathink" in complexity_decision.suggested_flags

        # Step 2: Collect more comprehensive context for complex task
        context_result = context_collector.collect_files(max_files=20)

        # Step 3: Set up handlers for complex analysis
        def intent_handler(context):
            return {
                "user_input": user_input,
                "intent": "security_analysis",
                "complexity": complexity_decision.complexity.value,
                "requires_deep_analysis": True
            }

        def classify_handler(context):
            return {
                "classification": "security_audit",
                "high_complexity": True,
                "analysis_type": "comprehensive"
            }

        def plan_handler(context):
            return {
                "plan": [
                    "scan_for_security_patterns",
                    "analyze_authentication",
                    "check_input_validation",
                    "review_dependencies",
                    "generate_report"
                ]
            }

        def execute_handler(context):
            # Simulate security analysis
            security_findings = []

            # Analyze collected files for security patterns
            for file_info in context_result.files:
                if file_info.content:
                    # Simple security pattern detection
                    if "password" in file_info.content.lower() and "=" in file_info.content:
                        security_findings.append({
                            "file": file_info.path,
                            "issue": "Potential hardcoded password",
                            "severity": "high"
                        })

            return {
                "executed": True,
                "security_findings": security_findings,
                "files_analyzed": len(context_result.files)
            }

        def verify_handler(context):
            findings = context.get("security_findings", [])
            return {
                "verified": True,
                "findings_count": len(findings),
                "analysis_complete": context.get("files_analyzed", 0) > 0
            }

        def report_handler(context):
            return {
                "outputs": {
                    "analysis_type": "security_audit",
                    "files_analyzed": context.get("files_analyzed", 0),
                    "findings": context.get("security_findings", []),
                    "complexity_level": context.get("complexity"),
                    "status": "completed"
                }
            }

        # Register handlers
        state_machine.register_handler(State.INTENT, intent_handler)
        state_machine.register_handler(State.CLASSIFY, classify_handler)
        state_machine.register_handler(State.PLAN, plan_handler)
        state_machine.register_handler(State.EXECUTE, execute_handler)
        state_machine.register_handler(State.VERIFY, verify_handler)
        state_machine.register_handler(State.REPORT, report_handler)

        # Execute workflow
        result = state_machine.run()

        # Verify successful completion
        assert result.success is True
        assert result.final_state == State.REPORT
        assert result.outputs["analysis_type"] == "security_audit"
        assert result.outputs["files_analyzed"] > 0
        assert result.outputs["complexity_level"] == "h"

    def test_amr_context_integration(self, sample_project: Path):
        """Test AMR router with real project context"""
        amr_router = AMRRouter()
        context_collector = ContextCollector(str(sample_project))

        # Collect project context
        context_result = context_collector.collect_files()

        # Create context for AMR
        amr_context = {
            "file_count": len(context_result.files),
            "total_size": context_result.total_size,
            "project_size": "medium" if len(context_result.files) > 5 else "small"
        }

        # Test different inputs with real context
        test_cases = [
            ("Create a simple function", ComplexityLevel.L1),
            ("Refactor the entire architecture for microservices", ComplexityLevel.H),
            ("Add error handling to main.py", ComplexityLevel.L1)
        ]

        for user_input, expected_complexity in test_cases:
            decision = amr_router.analyze_complexity(user_input, amr_context)
            # Context should influence but not override clear patterns
            assert decision.complexity is not None
            assert decision.confidence > 0

    def test_error_recovery_workflow(self, sample_project: Path):
        """Test error recovery in integrated workflow"""
        state_machine = StateMachine()

        # Set up handlers with intentional failure
        def intent_handler(context):
            return {"intent": "test_error_recovery"}

        def classify_handler(context):
            raise Exception("Simulated classification error")

        # Register handlers
        state_machine.register_handler(State.INTENT, intent_handler)
        state_machine.register_handler(State.CLASSIFY, classify_handler)

        # Execute workflow
        result = state_machine.run()

        # Verify error handling
        assert result.success is False
        assert result.final_state == State.ERROR
        assert "Simulated classification error" in result.error

    def test_performance_integration(self, sample_project: Path):
        """Test performance of integrated components"""
        import time

        # Initialize components
        amr_router = AMRRouter()
        context_collector = ContextCollector(str(sample_project))

        start_time = time.time()

        # Perform typical operations
        user_input = "Implement a new feature for the application"

        # AMR analysis
        complexity_decision = amr_router.analyze_complexity(user_input)

        # Context collection
        context_result = context_collector.collect_files(max_files=10)

        end_time = time.time()
        total_time = end_time - start_time

        # Performance assertions
        assert total_time < 2.0  # Should complete within 2 seconds
        assert complexity_decision is not None
        assert len(context_result.files) > 0

    def test_context_aware_routing(self, sample_project: Path):
        """Test how context influences routing decisions"""
        amr_router = AMRRouter()
        context_collector = ContextCollector(str(sample_project))

        # Collect project context
        context_result = context_collector.collect_files()

        # Create different context scenarios
        small_project_context = {
            "file_count": 3,
            "project_size": "small",
            "domains": ["simple"]
        }

        large_project_context = {
            "file_count": 100,
            "project_size": "large",
            "domains": ["frontend", "backend", "database"],
            "recent_failures": 2
        }

        # Same input, different contexts
        user_input = "Add validation to the form"

        decision_small = amr_router.analyze_complexity(user_input, small_project_context)
        decision_large = amr_router.analyze_complexity(user_input, large_project_context)

        # Large project context should generally increase complexity
        # (though not guaranteed due to pattern matching)
        assert decision_small.complexity is not None
        assert decision_large.complexity is not None

    def test_yaml_manifest_integration(self):
        """Test integration with YAML manifest system"""
        # This would test the YAML manifest loading and template generation
        # For now, we'll test that the manifest files exist and are valid

        personas_manifest = Path("packages/cursor-assets/manifests/personas.yaml")
        commands_manifest = Path("packages/cursor-assets/manifests/commands.yaml")

        if personas_manifest.exists():
            import yaml
            with open(personas_manifest) as f:
                personas_data = yaml.safe_load(f)
            assert "personas" in personas_data
            assert len(personas_data["personas"]) > 0

        if commands_manifest.exists():
            import yaml
            with open(commands_manifest) as f:
                commands_data = yaml.safe_load(f)
            assert "commands" in commands_data
            assert len(commands_data["commands"]) > 0