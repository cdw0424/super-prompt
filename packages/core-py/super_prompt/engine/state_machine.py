"""
State Machine - Fixed workflow execution (INTENT → TASK_CLASSIFY → PLAN → EXECUTE → VERIFY → REPORT)
"""

from enum import Enum
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import time


class WorkflowState(Enum):
    INTENT = "intent"
    TASK_CLASSIFY = "task_classify"
    PLAN = "plan"
    EXECUTE = "execute"
    VERIFY = "verify"
    REPORT = "report"


@dataclass
class WorkflowContext:
    """Context passed through workflow states"""
    session_id: str
    current_state: WorkflowState
    user_input: str
    metadata: Dict[str, Any]
    results: Dict[str, Any]
    start_time: float
    errors: list[str]


class StateMachine:
    """
    Fixed state machine for workflow execution.
    Ensures consistent, traceable execution flow.
    """

    def __init__(self):
        self.handlers: Dict[WorkflowState, Callable[[WorkflowContext], WorkflowContext]] = {}
        self.transitions = self._build_transitions()

    def register_handler(self, state: WorkflowState, handler: Callable[[WorkflowContext], WorkflowContext]):
        """Register a handler for a workflow state"""
        self.handlers[state] = handler

    def execute_workflow(self, user_input: str, session_id: Optional[str] = None) -> WorkflowContext:
        """Execute the complete workflow"""
        if not session_id:
            session_id = f"session_{int(time.time())}"

        context = WorkflowContext(
            session_id=session_id,
            current_state=WorkflowState.INTENT,
            user_input=user_input,
            metadata={},
            results={},
            start_time=time.time(),
            errors=[]
        )

        # Execute workflow through all states
        for state in self.transitions:
            if state in self.handlers:
                try:
                    context = self.handlers[state](context)
                    context.current_state = state
                except Exception as e:
                    context.errors.append(f"Error in {state.value}: {str(e)}")
                    break
            else:
                context.errors.append(f"No handler registered for {state.value}")
                break

        return context

    def _build_transitions(self) -> list[WorkflowState]:
        """Define the fixed state transition order"""
        return [
            WorkflowState.INTENT,
            WorkflowState.TASK_CLASSIFY,
            WorkflowState.PLAN,
            WorkflowState.EXECUTE,
            WorkflowState.VERIFY,
            WorkflowState.REPORT
        ]

    def get_workflow_status(self, context: WorkflowContext) -> Dict[str, Any]:
        """Get current workflow execution status"""
        elapsed = time.time() - context.start_time
        completed_states = []

        for state in self.transitions:
            if state.value in context.results:
                completed_states.append(state.value)
            else:
                break

        return {
            "session_id": context.session_id,
            "current_state": context.current_state.value,
            "completed_states": completed_states,
            "elapsed_time": elapsed,
            "errors": context.errors,
            "progress": len(completed_states) / len(self.transitions)
        }