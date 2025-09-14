"""
Tests for the state machine implementation
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from super_prompt.engine.state_machine import (
    StateMachine, State, StateTransition, ExecutionResult
)


class TestStateMachine:
    """Test cases for StateMachine class"""

    def test_initial_state(self, state_machine: StateMachine):
        """Test that state machine starts in INTENT state"""
        assert state_machine.current_state == State.INTENT
        assert state_machine.context == {}

    def test_register_handler(self, state_machine: StateMachine):
        """Test registering state handlers"""
        mock_handler = Mock(return_value={"test": "value"})

        state_machine.register_handler(State.INTENT, mock_handler)
        assert State.INTENT in state_machine.state_handlers
        assert state_machine.state_handlers[State.INTENT] == mock_handler

    def test_can_transition_normal_flow(self, state_machine: StateMachine):
        """Test normal state transitions"""
        # Default transitions should be set up
        assert state_machine.can_transition(State.INTENT, State.CLASSIFY)
        assert state_machine.can_transition(State.CLASSIFY, State.PLAN)
        assert state_machine.can_transition(State.PLAN, State.EXECUTE)
        assert state_machine.can_transition(State.EXECUTE, State.VERIFY)
        assert state_machine.can_transition(State.VERIFY, State.REPORT)

    def test_can_transition_invalid(self, state_machine: StateMachine):
        """Test invalid state transitions"""
        # These transitions should not be allowed
        assert not state_machine.can_transition(State.INTENT, State.EXECUTE)
        assert not state_machine.can_transition(State.REPORT, State.INTENT)
        assert not state_machine.can_transition(State.CLASSIFY, State.VERIFY)

    def test_transition_to_valid(self, state_machine: StateMachine):
        """Test successful state transition"""
        result = state_machine.transition_to(State.CLASSIFY)
        assert result is True
        assert state_machine.current_state == State.CLASSIFY

    def test_transition_to_invalid(self, state_machine: StateMachine):
        """Test failed state transition"""
        result = state_machine.transition_to(State.EXECUTE)
        assert result is False
        assert state_machine.current_state == State.INTENT  # Should not change

    def test_execute_current_state_success(self, state_machine: StateMachine):
        """Test successful state execution"""
        mock_handler = Mock(return_value={"result": "success", "data": 123})
        state_machine.register_handler(State.INTENT, mock_handler)

        result = state_machine.execute_current_state()

        assert result == {"result": "success", "data": 123}
        assert state_machine.context["result"] == "success"
        assert state_machine.context["data"] == 123
        mock_handler.assert_called_once()

    def test_execute_current_state_no_handler(self, state_machine: StateMachine):
        """Test state execution with no handler registered"""
        with pytest.raises(ValueError, match="No handler registered for state"):
            state_machine.execute_current_state()

    def test_execute_current_state_handler_error(self, state_machine: StateMachine):
        """Test state execution when handler raises exception"""
        mock_handler = Mock(side_effect=Exception("Handler error"))
        state_machine.register_handler(State.INTENT, mock_handler)

        result = state_machine.execute_current_state()

        assert "error" in result
        assert state_machine.context["execution_error"] is True
        assert "Handler error" in state_machine.context["error_message"]

    def test_run_complete_flow(self, state_machine: StateMachine):
        """Test complete state machine execution"""
        # Set up handlers for each state
        handlers = {
            State.INTENT: Mock(return_value={"intent": "create_component"}),
            State.CLASSIFY: Mock(return_value={"complexity": "medium"}),
            State.PLAN: Mock(return_value={"plan": "step1, step2, step3"}),
            State.EXECUTE: Mock(return_value={"execution": "completed"}),
            State.VERIFY: Mock(return_value={"verification": "passed"}),
            State.REPORT: Mock(return_value={"outputs": {"result": "success"}})
        }

        for state, handler in handlers.items():
            state_machine.register_handler(state, handler)

        # Run the state machine
        result = state_machine.run({"initial": "data"})

        # Verify successful completion
        assert result.success is True
        assert result.final_state == State.REPORT
        assert result.outputs == {"result": "success"}
        assert "initial" in result.context
        assert "intent" in result.context
        assert "complexity" in result.context

    def test_run_with_error(self, state_machine: StateMachine):
        """Test state machine execution with error"""
        # Set up handlers, with one that fails
        handlers = {
            State.INTENT: Mock(return_value={"intent": "test"}),
            State.CLASSIFY: Mock(side_effect=Exception("Classification failed")),
        }

        for state, handler in handlers.items():
            state_machine.register_handler(state, handler)

        # Run the state machine
        result = state_machine.run()

        # Verify error handling
        assert result.success is False
        assert result.final_state == State.ERROR
        assert "Classification failed" in result.error

    def test_run_max_iterations(self, state_machine: StateMachine):
        """Test state machine with infinite loop protection"""
        # Create a handler that doesn't advance state properly
        mock_handler = Mock(return_value={})
        state_machine.register_handler(State.INTENT, mock_handler)

        # Override _get_next_state to return None (no valid transition)
        state_machine._get_next_state = Mock(return_value=None)

        result = state_machine.run()

        assert result.success is False
        assert "Execution failed" in result.error

    def test_reset(self, state_machine: StateMachine):
        """Test state machine reset"""
        # Modify state and context
        state_machine.current_state = State.EXECUTE
        state_machine.context = {"test": "data"}

        # Reset
        state_machine.reset()

        # Verify reset
        assert state_machine.current_state == State.INTENT
        assert state_machine.context == {}

    def test_context_preservation(self, state_machine: StateMachine):
        """Test that context is preserved across state transitions"""
        # Set up handlers that modify context
        handlers = {
            State.INTENT: Mock(return_value={"step1": "done"}),
            State.CLASSIFY: Mock(return_value={"step2": "done"}),
            State.PLAN: Mock(return_value={"step3": "done"}),
        }

        for state, handler in handlers.items():
            state_machine.register_handler(state, handler)

        # Run through first few states
        initial_context = {"initial": "value"}
        state_machine.run(initial_context)

        # Context should contain all accumulated data
        assert "initial" in state_machine.context
        assert "step1" in state_machine.context
        assert "step2" in state_machine.context