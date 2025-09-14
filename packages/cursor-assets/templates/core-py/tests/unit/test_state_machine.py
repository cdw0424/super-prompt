"""
Unit tests for the state machine module.
"""

import pytest
from super_prompt.engine.state_machine import StateMachine, WorkflowState, WorkflowContext


class TestStateMachine:
    """Test cases for the StateMachine class."""

    def test_initialization(self):
        """Test that StateMachine initializes correctly."""
        sm = StateMachine()
        assert sm.handlers is not None
        assert sm.transitions is not None
        assert len(sm.transitions) == 6  # All workflow states

    def test_workflow_states_order(self):
        """Test that workflow states are in correct order."""
        sm = StateMachine()
        expected_order = [
            WorkflowState.INTENT,
            WorkflowState.TASK_CLASSIFY,
            WorkflowState.PLAN,
            WorkflowState.EXECUTE,
            WorkflowState.VERIFY,
            WorkflowState.REPORT
        ]
        assert sm.transitions == expected_order

    def test_register_handler(self):
        """Test registering a handler for a workflow state."""
        sm = StateMachine()

        def dummy_handler(context: WorkflowContext) -> WorkflowContext:
            return context

        sm.register_handler(WorkflowState.INTENT, dummy_handler)
        assert WorkflowState.INTENT in sm.handlers
        assert sm.handlers[WorkflowState.INTENT] == dummy_handler

    def test_execute_workflow_basic(self):
        """Test basic workflow execution."""
        sm = StateMachine()

        # Register a simple handler for each state
        def simple_handler(context: WorkflowContext) -> WorkflowContext:
            context.results[context.current_state.value] = {"processed": True}
            return context

        for state in sm.transitions:
            sm.register_handler(state, simple_handler)

        # Execute workflow
        result = sm.execute_workflow("test query")

        # Verify results
        assert result.user_input == "test query"
        assert result.session_id.startswith("session_")
        assert len(result.results) == 6  # All states processed

        for state in sm.transitions:
            assert state.value in result.results
            assert result.results[state.value]["processed"] is True

    def test_workflow_context_creation(self):
        """Test WorkflowContext creation and properties."""
        context = WorkflowContext(
            session_id="test_session",
            current_state=WorkflowState.INTENT,
            user_input="test input",
            metadata={"test": "data"},
            results={},
            start_time=1234567890.0,
            errors=[]
        )

        assert context.session_id == "test_session"
        assert context.current_state == WorkflowState.INTENT
        assert context.user_input == "test input"
        assert context.metadata["test"] == "data"
        assert context.results == {}
        assert context.start_time == 1234567890.0
        assert context.errors == []

    def test_error_handling_in_workflow(self):
        """Test error handling during workflow execution."""
        sm = StateMachine()

        def failing_handler(context: WorkflowContext) -> WorkflowContext:
            raise ValueError("Test error")

        def success_handler(context: WorkflowContext) -> WorkflowContext:
            context.results["success"] = True
            return context

        # Register failing handler for first state, success for others
        sm.register_handler(WorkflowState.INTENT, failing_handler)
        for state in sm.transitions[1:]:
            sm.register_handler(state, success_handler)

        result = sm.execute_workflow("test query")

        # Should have recorded the error
        assert len(result.errors) > 0
        assert "Test error" in str(result.errors[0])

        # Should not have processed subsequent states
        assert "task_classify" not in result.results

    def test_get_workflow_status(self):
        """Test getting workflow execution status."""
        sm = StateMachine()

        # Create a mock context
        context = WorkflowContext(
            session_id="test_session",
            current_state=WorkflowState.EXECUTE,
            user_input="test",
            metadata={},
            results={
                "intent": {"processed": True},
                "task_classify": {"processed": True},
                "plan": {"processed": True},
                "execute": {"processed": True}
            },
            start_time=100.0,
            errors=[]
        )

        # Mock the _calculate_elapsed_time method
        import time
        original_time = time.time
        time.time = lambda: 150.0  # 50 seconds elapsed

        try:
            status = sm.get_workflow_status(context)

            assert status["session_id"] == "test_session"
            assert status["current_state"] == "execute"
            assert len(status["completed_states"]) == 4
            assert status["progress"] == 4/6  # 4 out of 6 states completed
            assert status["elapsed_time"] == 50.0
        finally:
            time.time = original_time
