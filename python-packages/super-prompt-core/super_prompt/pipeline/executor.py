"""
Pipeline execution logic and state management
"""

import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

from .config import (
    PersonaPipelineConfig, 
    PipelineState, 
    DEFAULT_PLAN_LINES, 
    DEFAULT_EXEC_LINES,
    PIPELINE_ALIASES,
    PIPELINE_LABELS
)
from ..utils.span_manager import span_manager
from ..paths import project_root


def _analyze_project_context(project_dir: Union[str, Path], query: str) -> Dict[str, Any]:
    """Return minimal metadata for persona pipelines."""
    info: Dict[str, Any] = {"patterns": [], "query_relevance": []}
    try:
        root = Path(project_dir)
        if (root / ".cursor" / "mcp.json").exists():
            info["query_relevance"].append("cursor-mcp-config")
        if (root / "bin" / "sp-mcp").exists():
            info["query_relevance"].append("local-sp-mcp")
        lowered = (query or "").lower()
        for needle, tag in (
            ("mcp", "mcp"),
            ("cursor", "cursor"),
            ("tool", "tooling"),
            ("permission", "permissions"),
        ):
            if needle in lowered:
                info["patterns"].append(tag)
    except Exception:
        pass
    return info


def _build_plan_lines_from_state(persona: str, state: PipelineState) -> List[str]:
    """Build plan lines from current pipeline state"""
    dynamic: List[str] = []
    patterns = state.context_info.get("patterns") or []
    relevance = state.context_info.get("query_relevance") or []

    if not patterns:
        dynamic.append("- [dynamic] Collect repository signals (files, commands, patterns)")
    else:
        dynamic.append("- [dynamic] Focus areas: " + ", ".join(map(str, patterns[:3])))
    if relevance:
        dynamic.append("- [dynamic] Relevant entities: " + ", ".join(map(str, relevance[:5])))
    if state.codex_response:
        dynamic.append("- [dynamic] Incorporate Codex insights into hypotheses and checks")
    if state.persona_result_text:
        snippet = state.persona_result_text.strip().splitlines()[0][:160]
        if snippet:
            dynamic.append("- [dynamic] Persona insight: " + snippet)

    # Fallback defaults per persona
    base = list(
        DEFAULT_PLAN_LINES.get(
            persona,
            [
                "- Clarify requirements and constraints",
                "- Break down the problem into manageable steps",
                "- Identify risks and mitigation strategies",
            ],
        )
    )

    return (dynamic + base) if dynamic else base


def _build_exec_lines_from_state(persona: str, state: PipelineState) -> List[str]:
    """Build execution lines from current pipeline state"""
    dynamic: List[str] = []
    if state.errors:
        dynamic.append("- [dynamic] Address pipeline errors before proceeding")
    if state.decisions:
        dynamic.append("- [dynamic] Execute the agreed decision and capture evidence")
    if state.codex_response:
        dynamic.append("- [dynamic] Validate Codex-derived steps against ground truth")
    relevance = state.context_info.get("query_relevance") or []
    if relevance:
        dynamic.append("- [dynamic] Verify changes impacting: " + ", ".join(map(str, relevance[:5])))

    base = list(
        DEFAULT_EXEC_LINES.get(
            persona,
            [
                "- Implement prioritized actions",
                "- Validate outcomes against definition of done",
                "- Record follow-ups and monitor for regressions",
            ],
        )
    )

    return (dynamic + base) if dynamic else base


def _evaluate_gates(state: PipelineState) -> Tuple[bool, List[str]]:
    """Evaluate pipeline gates"""
    missing: List[str] = []
    patterns = state.context_info.get("patterns") or []
    relevance = state.context_info.get("query_relevance") or []

    if not patterns and not relevance:
        missing.append("context_signals")

    return (len(missing) == 0, missing)


def _safe_string(value: Any) -> str:
    """Convert value to safe string representation"""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


def _text_from(content: Any) -> str:
    """Extract text from various content types"""
    try:
        if hasattr(content, 'text'):
            return getattr(content, "text", "") or ""
    except Exception:
        pass
    return "" if content is None else str(content)


def run_persona_pipeline(
    config: PersonaPipelineConfig, query: str, extra_kwargs: Optional[Dict[str, Any]] = None
):
    """Execute a persona pipeline with the given configuration"""
    span_id = span_manager.start_span({"commandId": f"sp.{config.persona}-pipeline", "userId": None})
    try:
        if not query.strip():
            prompt = config.empty_prompt or (
                f"🔁 {config.label} pipeline activated.\n\nPlease provide a detailed query to begin the pipeline."
            )
            # Import TextContent from MCP module
            from ..mcp.version_detection import import_mcp_components
            try:
                _, TextContent, _ = import_mcp_components()
            except ImportError:
                from ..mcp.version_detection import create_fallback_mcp
                _, TextContent = create_fallback_mcp()
                
            return TextContent(type="text", text=prompt)

        project_dir = project_root()
        confession_logs: List[str] = []
        mem_overview = "no memory available"
        store = None
        
        try:
            from ..memory.store import MemoryStore
            store = MemoryStore.open(project_dir)
            recent = store.recent_events(limit=5)
            mem_overview = f"recent_events={len(recent)}"
        except Exception as exc:
            confession_logs.append(f"memory load skipped ({exc})")

        # Import codex assistance
        from ..codex.integration import summarize_situation_for_codex
        from ..codex.integration import call_codex_assistance
        from ..codex.integration import should_use_codex_assistance
        
        prompt_summary = summarize_situation_for_codex(query, "", config.persona)
        context_info = _analyze_project_context(project_dir, query)

        if config.use_codex is None:
            codex_needed = should_use_codex_assistance(query, config.persona)
        else:
            codex_needed = config.use_codex

        codex_response: Optional[str] = None
        if codex_needed:
            ctx_patterns = ", ".join(context_info.get("patterns", [])[:3])
            ctx_hint = f"Patterns: {ctx_patterns}" if ctx_patterns else ""
            codex_response = call_codex_assistance(query, ctx_hint, config.persona)

        persona_kwargs: Dict[str, Any] = {}
        if config.persona_kwargs:
            persona_kwargs.update(config.persona_kwargs)
        if extra_kwargs:
            persona_kwargs.update(extra_kwargs)

        persona_result = execute_persona(config.persona, query, **persona_kwargs)

        state = PipelineState(
            query=query,
            context_info=context_info,
            persona_result_text=_text_from(persona_result) or "",
            codex_response=codex_response,
            validation_logs=confession_logs or None,
            decisions=None,
            errors=None,
            todo=None,
        )

        # Gate before planning/execution
        gates_ok, missing = _evaluate_gates(state)
        if not gates_ok:
            plan_lines = [
                "- Collect repository signals (files, commands, patterns)",
                "- Re-run pipeline once context signals are available",
            ]
            exec_lines = [
                "- Blocked: prerequisite signals missing (" + ", ".join(missing) + ")",
                "- Address prerequisites, then resume from current stage",
            ]
        else:
            plan_lines = (
                config.plan_builder(query, context_info)
                if config.plan_builder
                else _build_plan_lines_from_state(config.persona, state)
            )
            exec_lines = (
                config.exec_builder(query, context_info)
                if config.exec_builder
                else _build_exec_lines_from_state(config.persona, state)
            )

        # Validation check
        try:
            from ..commands.validate_tools import validate_check
            audit = validate_check(project_root=project_dir)
            for line in (audit or {}).get("logs", []) or []:
                confession_logs.append(line)
        except Exception as exc:
            confession_logs.append(f"validation error: {exc}")

        # Build lightweight TODOs from plan
        try:
            previous_todo: Optional[List[Dict[str, Any]]] = None
            if store is not None:
                try:
                    recent_items = store.recent_events(limit=20)
                    for item in (recent_items or [])[::-1]:
                        data = item.get("data") if isinstance(item, dict) else None
                        tag = item.get("tag") if isinstance(item, dict) else None
                        payload = data or item
                        if tag == config.memory_tag and isinstance(payload, dict) and payload.get("todo"):
                            previous_todo = payload.get("todo")
                            break
                except Exception:
                    pass

            todo_list: List[Dict[str, Any]] = []
            # Seed from plan_lines
            for idx, step in enumerate(plan_lines):
                todo_list.append({"id": f"step-{idx+1}", "title": step, "status": "pending"})

            # If previous exists, advance next pending; else complete first as kickoff
            if previous_todo and isinstance(previous_todo, list):
                # Carry statuses and advance first pending
                advanced = False
                status_by_id = {t.get("id"): t.get("status") for t in previous_todo if isinstance(t, dict)}
                for t in todo_list:
                    sid = t.get("id")
                    if sid in status_by_id:
                        t["status"] = status_by_id[sid]
                for t in todo_list:
                    if t.get("status") == "pending" and not advanced:
                        t["status"] = "completed"
                        advanced = True
                        break
            else:
                if todo_list:
                    todo_list[0]["status"] = "completed"

            state.todo = todo_list
        except Exception:
            pass

        # Store pipeline state
        if store is not None:
            try:
                from ..memory.store import MemoryStore
                store.append_event(
                    config.memory_tag,
                    {
                        "persona": config.persona,
                        "query": query,
                        "patterns": context_info.get("patterns", []),
                        "plan": plan_lines,
                        "execution": exec_lines,
                        "codex_used": bool(codex_response),
                        "state": {
                            "relevance": context_info.get("query_relevance", []),
                            "codex": bool(codex_response),
                            "decisions": state.decisions or [],
                            "errors": state.errors or [],
                            "missing": missing if missing else [],
                        },
                        "todo": state.todo or [],
                    },
                )
            except Exception as exc:
                confession_logs.append(f"memory update skipped ({exc})")

        # Persist lightweight context into kv table for continuity
        try:
            pr = project_root()
            kv_db = Path(pr) / ".super-prompt" / "data" / "context_memory.db"
            kv_db.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(kv_db))
            conn.execute(
                "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at REAL NOT NULL)"
            )

            # Derive TODO progress and last error/decisions
            total_todo = len(state.todo or [])
            completed_todo = sum(1 for t in (state.todo or []) if t.get("status") == "completed")
            progress = f"{completed_todo}/{total_todo}" if total_todo else "0/0"
            last_error = (state.errors or [None])[-1] if (state.errors or []) else ""
            decisions_json = json.dumps(state.decisions or [], ensure_ascii=False)

            kv_items = {
                f"pipeline:last_persona:{config.persona}": config.persona,
                f"pipeline:last_query:{config.persona}": query,
                f"pipeline:last_patterns:{config.persona}": json.dumps(context_info.get("patterns", []), ensure_ascii=False),
                f"pipeline:last_relevance:{config.persona}": json.dumps(context_info.get("query_relevance", []), ensure_ascii=False),
                f"pipeline:has_codex:{config.persona}": "1" if codex_response else "0",
                f"pipeline:last_decisions:{config.persona}": decisions_json,
                f"pipeline:todo_counts:{config.persona}": progress,
                f"pipeline:last_error:{config.persona}": last_error or "",
            }
            now_ts = float(time.time())
            for k, v in kv_items.items():
                conn.execute(
                    "INSERT INTO kv(key, value, updated_at) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                    (k, str(v), now_ts),
                )
            conn.commit()
            conn.close()
        except Exception as exc:
            confession_logs.append(f"kv persist skipped ({exc})")

        # Build result output
        lines: List[str] = []
        lines.append(f"🧭 {config.label} Pipeline Result")
        lines.append("")
        lines.append("1) Prompt analysis")
        lines.append(prompt_summary)
        lines.append("")
        lines.append("2) Preliminary investigation")
        patterns = ", ".join(context_info.get("patterns", [])) or "n/a"
        relevance = ", ".join(context_info.get("query_relevance", [])) or "n/a"
        lines.append(f"- Patterns: {patterns}")
        lines.append(f"- Relevance: {relevance}")
        lines.append("")
        lines.append("3) Memory DB check")
        lines.append(f"- {mem_overview}")
        lines.append("")
        lines.append("4) Persona and command invocation")
        if codex_response:
            lines.append("- Codex Insight:")
            lines.append(codex_response)
        lines.append("- Persona Execution: complete")
        lines.append("")
        lines.append("5) Reasoning and Plan design")
        lines.extend(plan_lines)
        lines.append("")
        lines.append("6) Plan execution instructions")
        lines.extend(exec_lines)
        lines.append("")
        if state.decisions:
            lines.append("6.1) Decisions")
            for d in state.decisions:
                lines.append(f"- {d}")
            lines.append("")

        if state.todo:
            lines.append("10) TODO")
            for t in state.todo:
                status = t.get("status")
                mark = "[x]" if status == "completed" else "[ ]"
                lines.append(f"- {mark} {t.get('title')}")
            # Next action hint
            next_item = next((t for t in state.todo if t.get("status") == "pending"), None)
            if next_item:
                lines.append("")
                lines.append("Next → " + str(next_item.get("title")))
        lines.append("7) Confession double-check")
        if confession_logs:
            for log_line in confession_logs:
                lines.append(f"- {log_line}")
        else:
            lines.append("- validation log available (no issues)")
        lines.append("")
        lines.append("8) Memory DB update")
        lines.append("- pipeline event recorded")
        lines.append("")
        lines.append("9) Conclusion")
        lines.append(_text_from(persona_result))

        # Import TextContent from MCP module
        try:
            from ..mcp.version_detection import import_mcp_components
            _, TextContent, _ = import_mcp_components()
            result = TextContent(type="text", text="\n".join(lines).strip())
            return add_confession_mode(result, config.persona, query)
        except ImportError:
            from ..mcp.version_detection import create_fallback_mcp
            _, TextContent = create_fallback_mcp()
            result = TextContent(type="text", text="\n".join(lines).strip())
            return add_confession_mode(result, config.persona, query)
        except Exception as e:
            span_manager.end_span(span_id, "error", {"error": str(e)})
            raise
    except Exception as e:
        span_manager.end_span(span_id, "error", {"error": str(e)})
        raise
    except Exception as e:
        span_manager.end_span(span_id, "error", {"error": str(e)})
        raise


def execute_persona(persona: str, query: str, **kwargs: Any):
    """Execute a lightweight persona summary"""
    from .config import PIPELINE_LABELS
    
    config = get_pipeline_config(persona)
    label = config.label if config else persona.replace("-", " ").title()

    summary = query.strip() if isinstance(query, str) else ""
    summary = summary or "No request was entered."

    plan_preview = DEFAULT_PLAN_LINES.get(persona, [])[:3]
    exec_preview = DEFAULT_EXEC_LINES.get(persona, [])[:3]
    resources = get_persona_resource_links(persona)

    lines: List[str] = []
    lines.append(f"{label} Persona Assessment")
    lines.append("")
    lines.append("Request summary:")
    lines.append(f"- {summary}")

    filtered_kwargs = {k: v for k, v in kwargs.items() if v not in (None, "")}
    if filtered_kwargs:
        lines.append("")
        lines.append("Additional parameters:")
        for key, value in filtered_kwargs.items():
            lines.append(f"- {key}: {_safe_string(value)}")

    if plan_preview:
        lines.append("")
        lines.append("Plan preview:")
        for item in plan_preview:
            lines.append(item)

    if exec_preview:
        lines.append("")
        lines.append("Execution precautions:")
        for item in exec_preview:
            lines.append(item)

    if resources:
        lines.append("")
        lines.append(resources.strip())

    # Import TextContent from MCP module
    from ..mcp.version_detection import import_mcp_components
    try:
        _, TextContent, _ = import_mcp_components()
    except ImportError:
        from ..mcp.version_detection import create_fallback_mcp
        _, TextContent = create_fallback_mcp()

        span_manager.end_span(span_id, "ok")
        return TextContent(type="text", text="\n".join(lines).strip())
    except Exception as e:
        span_manager.end_span(span_id, "error", {"error": str(e)})
        raise
    except Exception as e:
        span_manager.end_span(span_id, "error", {"error": str(e)})
        raise


def add_confession_mode(result, persona: str, query: str):
    """Hook to annotate responses when confession/debug mode is enabled"""
    # Placeholder for future enhancements; currently acts as a pass-through.
    return result


def get_persona_resource_links(persona_name: str) -> str:
    """Return useful resource links for each persona"""
    resource_links = {
        "architect": """
📚 **Recommended Resources:**
• [System Design Interview](https://github.com/donnemartin/system-design-primer)
• [Designing Data-Intensive Applications](https://dataintensive.net/)
• [AWS Architecture Center](https://aws.amazon.com/architecture/)
• [Google Cloud Architecture Framework](https://cloud.google.com/architecture/framework)
""",
        "frontend": """
📚 **Recommended Resources:**
• [React Documentation](https://react.dev/)
• [Vue.js Guide](https://vuejs.org/guide/)
• [MDN Web Docs](https://developer.mozilla.org/)
• [Web.dev](https://web.dev/)
• [A11Y Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
""",
        "backend": """
📚 **Recommended Resources:**
• [REST API Design Best Practices](https://restfulapi.net/)
• [GraphQL Specification](https://spec.graphql.org/)
• [Database Design Tutorial](https://www.lucidchart.com/pages/database-diagram/database-design)
• [OWASP API Security](https://owasp.org/www-project-api-security/)
""",
        "security": """
📚 **Recommended Resources:**
• [OWASP Top 10](https://owasp.org/www-project-top-ten/)
• [MITRE CWE Database](https://cwe.mitre.org/)
• [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
• [SANS Security Policy Templates](https://www.sans.org/information-security-policy/)
""",
        "analyzer": """
📚 **Recommended Resources:**
• [Root Cause Analysis Guide](https://asq.org/quality-resources/root-cause-analysis)
• [Debugging Techniques](https://developers.google.com/web/tools/chrome-devtools)
• [Performance Analysis Tools](https://developer.chrome.com/docs/devtools/)
""",
    }
    return resource_links.get(persona_name, "")


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
        label="Translate",
        memory_tag="pipeline_translate",
        use_codex=False,
        empty_prompt="🌐 Translate pipeline activated. Please provide source text and target locale.",
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


def get_pipeline_config(persona: str) -> Optional[PersonaPipelineConfig]:
    """Get pipeline configuration for a persona"""
    return PIPELINE_CONFIGS.get(persona)
