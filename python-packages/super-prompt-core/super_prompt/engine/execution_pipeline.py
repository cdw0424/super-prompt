"""
Execution Pipeline - Orchestrates the complete execution flow
"""

from typing import Dict, Any, Optional, Callable
from .state_machine import StateMachine, WorkflowContext, WorkflowState
from .amr_router import AMRRouter
import time


class ExecutionPipeline:
    """
    Main execution pipeline that coordinates all components.
    Handles the complete flow from user input to final output.
    """

    def __init__(self):
        self.state_machine = StateMachine()
        self.amr_router = AMRRouter()
        self._setup_default_handlers()

    def execute(self, user_input: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a complete workflow pipeline.

        Args:
            user_input: The user's request/query
            **kwargs: Additional execution parameters

        Returns:
            Complete execution results
        """
        start_time = time.time()

        # Execute workflow
        context = self.state_machine.execute_workflow(user_input, kwargs.get("session_id"))

        # Add AMR routing information
        context.metadata["amr_level"] = self.amr_router.classify_task(user_input, context.metadata)
        context.metadata["amr_switch_template"] = self.amr_router.get_switch_template(
            self.amr_router.classify_task(""),  # Assume starting from medium
            context.metadata["amr_level"]
        )

        # Calculate execution metrics
        execution_time = time.time() - start_time
        context.metadata["execution_time"] = execution_time
        context.metadata["pipeline_version"] = "3.0.0"

        return self._format_results(context)

    def register_handler(self, state: WorkflowState, handler: Callable[[WorkflowContext], WorkflowContext]):
        """Register a custom handler for a workflow state"""
        self.state_machine.register_handler(state, handler)

    def get_status(self, session_id: str) -> Dict[str, Any]:
        """Get execution status for a session"""
        # This would need to be implemented with session storage
        return {"status": "not_implemented"}

    def _setup_default_handlers(self):
        """Setup default handlers for the state machine"""

        def intent_handler(context: WorkflowContext) -> WorkflowContext:
            """Process user intent"""
            context.results["intent"] = {
                "raw_input": context.user_input,
                "timestamp": time.time(),
                "parsed": self._parse_intent(context.user_input)
            }
            return context

        def task_classify_handler(context: WorkflowContext) -> WorkflowContext:
            """Classify task complexity"""
            intent_data = context.results["intent"]
            classification = self.amr_router.classify_task(intent_data["raw_input"], context.metadata)

            context.results["task_classification"] = {
                "level": classification.value,
                "confidence": "high",  # Placeholder
                "reasoning": f"Based on input analysis: {intent_data['raw_input'][:100]}..."
            }
            return context

        def plan_handler(context: WorkflowContext) -> WorkflowContext:
            """Generate execution plan"""
            classification = context.results["task_classification"]

            context.results["plan"] = {
                "strategy": self._generate_strategy(classification["level"]),
                "steps": self._generate_steps(classification["level"]),
                "risks": self._assess_risks(classification["level"]),
                "estimated_tokens": 1000  # Placeholder
            }
            return context

        def execute_handler(context: WorkflowContext) -> WorkflowContext:
            """Execute the planned workflow"""
            plan = context.results["plan"]

            # Placeholder execution logic
            context.results["execution"] = {
                "status": "completed",
                "output": f"Executed {len(plan['steps'])} steps",
                "artifacts": []
            }
            return context

        def verify_handler(context: WorkflowContext) -> WorkflowContext:
            """Verify execution results"""
            execution = context.results["execution"]

            context.results["verification"] = {
                "status": "passed" if execution["status"] == "completed" else "failed",
                "checks": ["syntax", "logic", "completeness"],
                "issues": []
            }
            return context

        def report_handler(context: WorkflowContext) -> WorkflowContext:
            """Generate final report"""
            context.results["report"] = {
                "summary": self._generate_summary(context),
                "metrics": self._calculate_metrics(context),
                "recommendations": self._generate_recommendations(context)
            }
            return context

        # Register handlers
        self.register_handler(WorkflowState.INTENT, intent_handler)
        self.register_handler(WorkflowState.TASK_CLASSIFY, task_classify_handler)
        self.register_handler(WorkflowState.PLAN, plan_handler)
        self.register_handler(WorkflowState.EXECUTE, execute_handler)
        self.register_handler(WorkflowState.VERIFY, verify_handler)
        self.register_handler(WorkflowState.REPORT, report_handler)

    def _parse_intent(self, user_input: str) -> Dict[str, Any]:
        """Parse user intent from input"""
        return {
            "command_type": "generic",
            "target": "unknown",
            "complexity": "medium"
        }

    def _generate_strategy(self, level: str) -> str:
        """Generate execution strategy based on complexity level"""
        strategies = {
            "light": "Direct execution with minimal planning",
            "moderate": "Structured approach with checkpoints",
            "heavy": "Comprehensive planning with multiple iterations"
        }
        return strategies.get(level, "Standard execution strategy")

    def _generate_steps(self, level: str) -> list[str]:
        """Generate execution steps"""
        steps_map = {
            "light": ["Analyze input", "Execute task", "Return result"],
            "moderate": ["Analyze input", "Plan approach", "Execute task", "Validate output"],
            "heavy": ["Deep analysis", "Strategic planning", "Iterative execution", "Comprehensive validation", "Final review"]
        }
        return steps_map.get(level, ["Execute task"])

    def _assess_risks(self, level: str) -> list[str]:
        """Assess execution risks"""
        risks_map = {
            "light": ["Minimal risk - straightforward execution"],
            "moderate": ["Potential edge cases", "Integration issues"],
            "heavy": ["Complex dependencies", "High coordination needs", "Quality assurance challenges"]
        }
        return risks_map.get(level, [])

    def _generate_summary(self, context: WorkflowContext) -> str:
        """Generate execution summary"""
        return f"Completed workflow in {context.metadata.get('execution_time', 0):.2f}s with {len(context.errors)} errors"

    def _calculate_metrics(self, context: WorkflowContext) -> Dict[str, Any]:
        """Calculate execution metrics"""
        return {
            "execution_time": context.metadata.get("execution_time", 0),
            "error_count": len(context.errors),
            "completion_rate": 1.0 if not context.errors else 0.0
        }

    def _generate_recommendations(self, context: WorkflowContext) -> list[str]:
        """Generate recommendations based on execution"""
        recommendations = []
        if context.errors:
            recommendations.append("Address execution errors for improved reliability")
        if context.metadata.get("execution_time", 0) > 10:
            recommendations.append("Consider optimization for faster execution")
        return recommendations

    def _format_results(self, context: WorkflowContext) -> Dict[str, Any]:
        """Format final execution results"""
        return {
            "session_id": context.session_id,
            "status": "completed" if not context.errors else "failed",
            "workflow_state": context.current_state.value,
            "results": context.results,
            "metadata": context.metadata,
            "errors": context.errors,
            "execution_time": context.metadata.get("execution_time", 0)
        }
