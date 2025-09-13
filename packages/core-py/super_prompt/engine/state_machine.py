"""
State Machine Implementation

Implements the core state machine for Super Prompt execution:
INTENT → CLASSIFY → PLAN → EXECUTE → VERIFY → REPORT
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)


class State(Enum):
    """Core states in the Super Prompt execution flow"""
    INTENT = "intent"           # Parse user intent and requirements
    CLASSIFY = "classify"       # Classify complexity and routing needs
    PLAN = "plan"              # Create execution plan
    EXECUTE = "execute"        # Execute the planned actions
    VERIFY = "verify"          # Verify results and quality
    REPORT = "report"          # Generate final report
    ERROR = "error"            # Error state for recovery


@dataclass
class StateTransition:
    """Represents a transition between states with conditions"""
    from_state: State
    to_state: State
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None


@dataclass
class ExecutionResult:
    """Result of state machine execution"""
    success: bool
    final_state: State
    context: Dict[str, Any]
    error: Optional[str] = None
    outputs: Optional[Dict[str, Any]] = None


class StateMachine:
    """
    Core state machine for Super Prompt execution

    Manages the flow through: INTENT → CLASSIFY → PLAN → EXECUTE → VERIFY → REPORT
    with error handling and recovery mechanisms.
    """

    def __init__(self):
        self.current_state = State.INTENT
        self.context: Dict[str, Any] = {}
        self.transitions: List[StateTransition] = []
        self.state_handlers: Dict[State, Callable] = {}
        self._setup_default_transitions()

    def _setup_default_transitions(self):
        """Setup default state transitions"""
        self.transitions = [
            # Normal flow
            StateTransition(State.INTENT, State.CLASSIFY),
            StateTransition(State.CLASSIFY, State.PLAN),
            StateTransition(State.PLAN, State.EXECUTE),
            StateTransition(State.EXECUTE, State.VERIFY),
            StateTransition(State.VERIFY, State.REPORT),
        ]

    def register_handler(self, state: State, handler: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """Register a handler for a specific state"""
        self.state_handlers[state] = handler

    def can_transition(self, from_state: State, to_state: State) -> bool:
        """Check if transition is allowed"""
        for transition in self.transitions:
            if (transition.from_state == from_state and
                transition.to_state == to_state):
                if transition.condition is None:
                    return True
                return transition.condition(self.context)
        return False

    def transition_to(self, new_state: State) -> bool:
        """Attempt to transition to a new state"""
        if not self.can_transition(self.current_state, new_state):
            logger.warning(f"Invalid transition from {self.current_state} to {new_state}")
            return False

        logger.info(f"Transitioning from {self.current_state} to {new_state}")
        self.current_state = new_state
        return True

    def execute_current_state(self) -> Dict[str, Any]:
        """Execute the current state's handler"""
        if self.current_state not in self.state_handlers:
            raise ValueError(f"No handler registered for state {self.current_state}")

        logger.info(f"Executing state: {self.current_state}")
        try:
            result = self.state_handlers[self.current_state](self.context.copy())
            if result:
                self.context.update(result)
            return result or {}
        except Exception as e:
            logger.error(f"Error executing state {self.current_state}: {e}")
            self.context['execution_error'] = True
            self.context['error_message'] = str(e)
            return {'error': str(e)}

    def run(self, initial_context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """Run the state machine from INTENT to completion"""
        if initial_context:
            self.context.update(initial_context)

        self.current_state = State.INTENT
        max_iterations = 20
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            try:
                state_result = self.execute_current_state()
                self.context.update(state_result)
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    final_state=State.ERROR,
                    context=self.context,
                    error=str(e)
                )

            if self.current_state == State.REPORT:
                return ExecutionResult(
                    success=True,
                    final_state=State.REPORT,
                    context=self.context,
                    outputs=self.context.get('outputs', {})
                )

            if self.current_state == State.ERROR:
                return ExecutionResult(
                    success=False,
                    final_state=State.ERROR,
                    context=self.context,
                    error=self.context.get('error_message', 'Unknown error')
                )

            next_state = self._get_next_state()
            if next_state is None or not self.transition_to(next_state):
                break

        return ExecutionResult(
            success=False,
            final_state=self.current_state,
            context=self.context,
            error="Execution failed"
        )

    def _get_next_state(self) -> Optional[State]:
        """Determine the next state based on current state and context"""
        for transition in self.transitions:
            if transition.from_state == self.current_state:
                if transition.condition is None or transition.condition(self.context):
                    return transition.to_state
        return None

    def reset(self):
        """Reset the state machine to initial state"""
        self.current_state = State.INTENT
        self.context.clear()