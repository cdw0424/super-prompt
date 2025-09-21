# packages/core-py/super_prompt/personas/pipeline_manager.py
"""
페르소나 파이프라인 관리 및 실행
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Union, Tuple

from ..core.memory_manager import progress
from ..analysis.project_analyzer import analyze_project_context
from ..codex.integration import call_codex_assistance, should_use_codex_assistance, summarize_situation_for_codex
from ..sdd.architecture import generate_sdd_persona_overlay
from ..prompts.workflow_executor import run_prompt_based_workflow


@dataclass
class PersonaPipelineConfig:
    persona: str
    label: str
    memory_tag: str
    use_codex: Optional[bool] = None
    plan_builder: Optional[Callable[[str, dict], List[str]]] = None
    exec_builder: Optional[Callable[[str, dict], List[str]]] = None
    persona_kwargs: Optional[Dict[str, Any]] = None
    empty_prompt: Optional[str] = None


@dataclass
class PipelineState:
    query: str
    context_info: Dict[str, Any]
    persona_result_text: str
    codex_response: Optional[str] = None
    validation_logs: Optional[List[str]] = None
    decisions: Optional[List[str]] = None
    errors: Optional[List[str]] = None
    todo: Optional[List[Dict[str, Any]]] = None


# Pipeline configurations
PIPELINE_CONFIGS: Dict[str, PersonaPipelineConfig] = {
    "architect": PersonaPipelineConfig(
        persona="architect",
        label="Architect",
        memory_tag="pipeline_architect",
        empty_prompt="🏗️ Architect pipeline activated. Describe the system or feature to design.",
    ),
    "frontend": PersonaPipelineConfig(
        persona="frontend",
        label="Frontend",
        memory_tag="pipeline_frontend",
        empty_prompt="🎨 Frontend pipeline activated. Share the UI/UX issue to analyze.",
    ),
    "backend": PersonaPipelineConfig(
        persona="backend",
        label="Backend",
        memory_tag="pipeline_backend",
        empty_prompt="⚙️ Backend pipeline activated. Provide the backend/API context to review.",
    ),
    "security": PersonaPipelineConfig(
        persona="security",
        label="Security",
        memory_tag="pipeline_security",
        use_codex=True,
        empty_prompt="🛡️ Security pipeline activated. Describe the threat or vulnerability.",
    ),
    "performance": PersonaPipelineConfig(
        persona="performance",
        label="Performance",
        memory_tag="pipeline_performance",
        empty_prompt="⚡ Performance pipeline activated. Provide the workload to optimize.",
    ),
    "analyzer": PersonaPipelineConfig(
        persona="analyzer",
        label="Analyzer",
        memory_tag="pipeline_analyzer",
        use_codex=True,
        empty_prompt="🔍 Analyzer pipeline activated. Describe the incident or defect to investigate.",
    ),
    "qa": PersonaPipelineConfig(
        persona="qa",
        label="QA",
        memory_tag="pipeline_qa",
        empty_prompt="🧪 QA pipeline activated. Outline the feature or risk area to test.",
    ),
    "refactorer": PersonaPipelineConfig(
        persona="refactorer",
        label="Refactorer",
        memory_tag="pipeline_refactorer",
        empty_prompt="🔧 Refactorer pipeline activated. Describe the code area to improve.",
    ),
    "devops": PersonaPipelineConfig(
        persona="devops",
        label="DevOps",
        memory_tag="pipeline_devops",
        empty_prompt="🚢 DevOps pipeline activated. Provide the infra or deployment concern.",
    ),
    "debate": PersonaPipelineConfig(
        persona="debate",
        label="Debate",
        memory_tag="pipeline_debate",
        empty_prompt="💬 Debate pipeline activated. Provide the decision topic to evaluate.",
    ),
    "mentor": PersonaPipelineConfig(
        persona="mentor",
        label="Mentor",
        memory_tag="pipeline_mentor",
        empty_prompt="👨‍🏫 Mentor pipeline activated. Share the learning goal or question.",
    ),
    "scribe": PersonaPipelineConfig(
        persona="scribe",
        label="Scribe",
        memory_tag="pipeline_scribe",
        persona_kwargs={"lang": "en"},
        empty_prompt="📝 Scribe pipeline activated. Provide the documentation task.",
    ),
    "dev": PersonaPipelineConfig(
        persona="dev",
        label="Dev",
        memory_tag="pipeline_dev",
        empty_prompt="🚀 Dev pipeline activated. Describe the feature or bug fix to implement.",
    ),
    "implement": PersonaPipelineConfig(
        persona="implement",
        label="Implement",
        memory_tag="pipeline_implement",
        empty_prompt="🛠️ Implement pipeline activated. Provide the executable steps or code changes to deliver.",
    ),
    "grok": PersonaPipelineConfig(
        persona="grok",
        label="Grok",
        memory_tag="pipeline_grok",
        empty_prompt="🤖 Grok pipeline activated. Provide the query to explore in Grok mode.",
    ),
    "db-expert": PersonaPipelineConfig(
        persona="db-expert",
        label="DB Expert",
        memory_tag="pipeline_db_expert",
        empty_prompt="🗄️ DB Expert pipeline activated. Share the schema or query challenge.",
    ),
    "optimize": PersonaPipelineConfig(
        persona="optimize",
        label="Optimize",
        memory_tag="pipeline_optimize",
        empty_prompt="🎯 Optimize pipeline activated. Describe the system or metric to improve.",
    ),
    "review": PersonaPipelineConfig(
        persona="review",
        label="Review",
        memory_tag="pipeline_review",
        empty_prompt="📋 Review pipeline activated. Provide the diff or component to review.",
    ),
    "service-planner": PersonaPipelineConfig(
        persona="service-planner",
        label="Service Planner",
        memory_tag="pipeline_service_planner",
        use_codex=True,
        empty_prompt="🧭 Service Planner pipeline activated. Outline the service or product goal.",
    ),
    "tr": PersonaPipelineConfig(
        persona="tr",
        label="Troubleshooting",
        memory_tag="pipeline_troubleshooting",
        use_codex=True,
        empty_prompt="🛠️ Troubleshooting pipeline activated. Describe the incident, symptoms, or failing task to diagnose.",
    ),
    "doc-master": PersonaPipelineConfig(
        persona="doc-master",
        label="Doc Master",
        memory_tag="pipeline_doc_master",
        empty_prompt="📚 Doc Master pipeline activated. Provide the documentation architecture task.",
    ),
    "docs-refector": PersonaPipelineConfig(
        persona="docs-refector",
        label="Docs Refector",
        memory_tag="pipeline_docs_refector",
        empty_prompt="🗂️ Docs Refector pipeline activated. Describe docs to consolidate.",
    ),
    "ultracompressed": PersonaPipelineConfig(
        persona="ultracompressed",
        label="Ultra Compressed",
        memory_tag="pipeline_ultracompressed",
        empty_prompt="🗜️ Ultra Compressed pipeline activated. Provide the topic to compress.",
    ),
    "seq": PersonaPipelineConfig(
        persona="seq",
        label="Sequential",
        memory_tag="pipeline_seq",
        empty_prompt="🔍 Sequential pipeline activated. Specify the problem to analyze step-by-step.",
    ),
    "seq-ultra": PersonaPipelineConfig(
        persona="seq-ultra",
        label="Sequential Ultra",
        memory_tag="pipeline_seq_ultra",
        empty_prompt="🧠 Sequential Ultra pipeline activated. Provide the complex scenario to dissect.",
    ),
    "high": PersonaPipelineConfig(
        persona="high",
        label="High Reasoning",
        memory_tag="pipeline_high",
        use_codex=True,
        empty_prompt="🧠 High Reasoning pipeline activated. Share the strategic question to explore.",
    ),
}


class PersonaPipeline:
    """
    Pipeline for running persona analysis
    """

    def __init__(self):
        from ..core.memory_manager import span_manager
        self.span_manager = span_manager

    def run_persona(self, persona_name: str, query: str):
        """
        Run a persona analysis for the given query

        Args:
            persona_name: Name of the persona to run
            query: The query to analyze

        Returns:
            Result object with text attribute
        """
        try:
            # Create a span for this persona analysis
            span_id = self.span_manager.start_span({
                "commandId": f"persona_{persona_name}",
                "userId": None
            })

            try:
                # Get the persona configuration
                config = PIPELINE_CONFIGS.get(persona_name)
                if not config:
                    raise ValueError(f"Unknown persona: {persona_name}")

                prompt_output = run_prompt_based_workflow(persona_name, query)

                if not prompt_output or prompt_output.startswith("Error:"):
                    fallback_reason = prompt_output if prompt_output else "Prompt template unavailable"
                    prompt_output = (
                        f"Persona '{persona_name}' fallback response for query: "
                        f"{query[:100]}{'...' if len(query) > 100 else ''}.\n"
                        f"Reason: {fallback_reason}"
                    )

                result_text = f"[{persona_name.upper()}] Analysis Prompt Generated:\n\n{prompt_output}"

                sdd_overlay = generate_sdd_persona_overlay(persona_name, query)
                if sdd_overlay:
                    result_text = f"{result_text}\n\n---\n{sdd_overlay}"

                result = type('Result', (), {'text': result_text})()

                self.span_manager.end_span(span_id, "ok")
                return result

            except Exception as inner_e:
                self.span_manager.end_span(span_id, "error", {"error": str(inner_e)})
                raise

        except Exception as e:
            # Return error result
            error_text = f"Persona analysis error: {str(e)}"
            return type('Result', (), {'text': error_text})()



# Pipeline aliases
PIPELINE_ALIASES: Dict[str, str] = {
    "architect": "architect",
    "architecture": "architect",
    "frontend": "frontend",
    "ui": "frontend",
    "backend": "backend",
    "api": "backend",
    "security": "security",
    "performance": "performance",
    "perf": "performance",
    "analyzer": "analyzer",
    "analysis": "analyzer",
    "qa": "qa",
    "quality": "qa",
    "refactor": "refactorer",
    "refactorer": "refactorer",
    "devops": "devops",
    "debate": "debate",
    "mentor": "mentor",
    "scribe": "scribe",
    "doc": "doc-master",
    "doc-master": "doc-master",
    "docs-refector": "docs-refector",
    "dev": "dev",
    "implement": "implement",
    "grok": "grok",
    "db-expert": "db-expert",
    "database": "db-expert",
    "optimize": "optimize",
    "optimization": "optimize",
    "review": "review",
    "code-review": "review",
    "service-planner": "service-planner",
    "service": "service-planner",
    "translate": "tr",
    "translator": "tr",
    "troubleshoot": "tr",
    "trouble": "tr",
    "tr": "tr",
    "ultra": "ultracompressed",
    "ultracompressed": "ultracompressed",
    "seq": "seq",
    "sequential": "seq",
    "seq-ultra": "seq-ultra",
    "high": "high",
}


# Pipeline labels
PIPELINE_LABELS: Dict[str, str] = {
    "architect": "Architect",
    "frontend": "Frontend",
    "backend": "Backend",
    "security": "Security",
    "performance": "Performance",
    "analyzer": "Analyzer",
    "qa": "QA",
    "refactorer": "Refactorer",
    "devops": "DevOps",
    "debate": "Debate",
    "mentor": "Mentor",
    "scribe": "Scribe",
    "dev": "Dev",
    "implement": "Implement",
    "grok": "Grok",
    "db-expert": "DB Expert",
    "optimize": "Optimize",
    "review": "Review",
    "service-planner": "Service Planner",
    "tr": "Troubleshooting",
    "doc-master": "Doc Master",
    "docs-refector": "Docs Refector",
    "ultracompressed": "Ultra Compressed",
    "seq": "Sequential",
    "seq-ultra": "Sequential Ultra",
    "high": "High Reasoning",
}
