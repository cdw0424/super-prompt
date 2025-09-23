# packages/core-py/super_prompt/mcp_app.py
# Complete MCP application with all Super Prompt v5.0.5 personas

import json
import os

from .prompts.workflow_executor import run_prompt_based_workflow
from .codex.client import run_codex_high_with_fallback
from .context.collector import ContextCollector
from .personas.pipeline_manager import PersonaPipeline
from .high_mode import is_high_mode_enabled


def _format_codex_context(context_result, max_files: int = 6, snippet_chars: int = 600, max_chars: int = 8000) -> str:
    """Convert collected context into a compact digest for Codex prompts."""

    if not context_result:
        return ""

    files = list(context_result.get("files") or [])
    if not files:
        return ""

    selected = files[:max_files]
    header_paths = ", ".join(part.get("path", "") for part in selected if part.get("path"))
    sections = []
    if header_paths:
        sections.append(f"Focus files: {header_paths}")

    for idx, part in enumerate(selected, start=1):
        path = part.get("path", "unknown") or "unknown"
        snippet = (part.get("content") or "").strip()
        if not snippet:
            continue
        snippet = snippet.replace("```", "``")
        if len(snippet) > snippet_chars:
            snippet = snippet[:snippet_chars] + "..."
        sections.append(f"[{idx}] {path}\n{snippet}")

    digest = "\n\n".join(sections).strip()
    if not digest:
        return ""
    if len(digest) > max_chars:
        digest = digest[:max_chars] + "\n\n[context truncated]"
    return digest


def _normalize_query(query: str) -> str:
    """Normalize user query by stripping whitespace and handling empty queries"""
    if not query or not isinstance(query, str):
        return ""
    return query.strip()


def create_app():
    """Factory function that creates and configures FastMCP app with all personas"""
    try:
        from mcp.server.fastmcp import FastMCP
        app = FastMCP(name="super-prompt")
    except ImportError:
        raise RuntimeError("MCP SDK not available")

    # High-level strategic analysis
    @app.tool(name="sp_high")
    def high(query: str, persona: str = "high", force_codex: bool = False) -> str:
        """High-effort planning powered by Codex (plan-first execution)."""

        force = force_codex
        if not isinstance(force, bool):
            force = str(force).strip().lower() in {"1", "true", "yes", "on"}

        if not force and not is_high_mode_enabled():
            use_pipeline = os.getenv("USE_PIPELINE", "false").lower() == "true"
            if not use_pipeline:
                try:
                    return run_prompt_based_workflow("high", query)
                except Exception:
                    use_pipeline = True

            if use_pipeline:
                pipeline = PersonaPipeline()
                result = pipeline.run_persona("high", query)
                return result.text if hasattr(result, "text") else str(result)

        collector = ContextCollector()
        context_result = collector.collect_context(query, max_tokens=8000)
        context_digest = _format_codex_context(context_result)

        plan_output = run_codex_high_with_fallback(query=query, context=context_digest, persona=persona)
        if isinstance(plan_output, dict):
            return json.dumps(plan_output, ensure_ascii=False)
        return plan_output

    # Systematic root cause analysis
    @app.tool(name="sp_analyzer")
    def analyzer(query: str, persona: str = "analyzer") -> str:
        """Systematic root cause analysis: Evidence-based problem analysis and causal relationships"""
        return run_prompt_based_workflow("analyzer", query)

    # System architecture design
    @app.tool(name="sp_architect")
    def architect(query: str, persona: str = "architect") -> str:
        """System architecture design: Scalable architecture, technology stacks, and design patterns"""
        return run_prompt_based_workflow("architect", query)

    # Backend development
    @app.tool(name="sp_backend")
    def backend(query: str, persona: str = "backend") -> str:
        """Backend development: APIs, databases, security, and performance optimization"""
        return run_prompt_based_workflow("backend", query)

    # Frontend development
    @app.tool(name="sp_frontend")
    def frontend(query: str, persona: str = "frontend") -> str:
        """Frontend development: UI/UX, responsive design, accessibility, and performance"""
        return run_prompt_based_workflow("frontend", query)

    # General development
    @app.tool(name="sp_dev")
    def dev(query: str, persona: str = "dev") -> str:
        """Full-stack development: Implementation planning, code quality, and deployment"""
        return run_prompt_based_workflow("dev", query)

    # Security analysis
    @app.tool(name="sp_security")
    def security(query: str, persona: str = "security") -> str:
        """Security analysis: Threat modeling, security controls, and compliance"""
        return run_prompt_based_workflow("security", query)

    # Performance optimization
    @app.tool(name="sp_performance")
    def performance(query: str, persona: str = "performance") -> str:
        """Performance analysis: Bottleneck identification, optimization strategies, and monitoring"""
        return run_prompt_based_workflow("performance", query)

    # Quality assurance
    @app.tool(name="sp_qa")
    def qa(query: str, persona: str = "qa") -> str:
        """Quality assurance: Testing strategies, automation, and quality metrics"""
        return run_prompt_based_workflow("qa", query)

    # DevOps engineering
    @app.tool(name="sp_devops")
    def devops(query: str, persona: str = "devops") -> str:
        """DevOps engineering: CI/CD, infrastructure, monitoring, and automation"""
        return run_prompt_based_workflow("devops", query)

    # Code refactoring
    @app.tool(name="sp_refactorer")
    def refactorer(query: str, persona: str = "refactorer") -> str:
        """Code refactoring: Technical debt reduction, design pattern application, and code quality"""
        return run_prompt_based_workflow("refactorer", query)

    # Documentation
    @app.tool(name="sp_doc_master")
    def doc_master(query: str, persona: str = "doc_master") -> str:
        """Documentation architecture: Technical writing, content organization, and documentation strategy"""
        return run_prompt_based_workflow("doc_master", query)

    # Database expertise
    @app.tool(name="sp_db_expert")
    def db_expert(query: str, persona: str = "db_expert") -> str:
        """Database architecture: Schema design, performance optimization, and scalability"""
        return run_prompt_based_workflow("db_expert", query)

    # Code review
    @app.tool(name="sp_review")
    def review(query: str, persona: str = "review") -> str:
        """Code review: Quality assessment, security analysis, and improvement recommendations"""
        return run_prompt_based_workflow("review", query)

    # Implementation planning
    @app.tool(name="sp_implement")
    def implement(query: str, persona: str = "implement") -> str:
        """Implementation planning: Requirements breakdown, technical approach, and deployment strategy"""
        return run_prompt_based_workflow("implement", query)

    # Developer mentoring
    @app.tool(name="sp_mentor")
    def mentor(query: str, persona: str = "mentor") -> str:
        """Developer mentoring: Skill development, best practices, and career guidance"""
        return run_prompt_based_workflow("mentor", query)

    # Technical writing
    @app.tool(name="sp_scribe")
    def scribe(query: str, persona: str = "scribe") -> str:
        """Technical writing: Documentation creation, content structure, and communication"""
        return run_prompt_based_workflow("scribe", query)

    # Strategic debate
    @app.tool(name="sp_debate")
    def debate(query: str, persona: str = "debate") -> str:
        """Strategic debate: Multiple perspectives, critical analysis, and balanced conclusions"""
        return run_prompt_based_workflow("debate", query)

    # Performance optimization
    @app.tool(name="sp_optimize")
    def optimize(query: str, persona: str = "optimize") -> str:
        """Performance optimization: System analysis, bottleneck resolution, and monitoring setup"""
        return run_prompt_based_workflow("optimize", query)

    # Project planning
    @app.tool(name="sp_plan")
    def plan(query: str, persona: str = "plan") -> str:
        """Project planning: Scope definition, timeline planning, and risk assessment"""
        return run_prompt_based_workflow("plan", query)

    # Task management
    @app.tool(name="sp_tasks")
    def tasks(query: str, persona: str = "tasks") -> str:
        """Task management: Work breakdown, priority assignment, and progress tracking"""
        return run_prompt_based_workflow("tasks", query)

    # Requirements specification
    @app.tool(name="sp_specify")
    def specify(query: str, persona: str = "specify") -> str:
        """Requirements specification: Requirements gathering, validation, and documentation"""
        return run_prompt_based_workflow("specify", query)

    # Sequential reasoning
    @app.tool(name="sp_seq")
    def seq(query: str, persona: str = "seq") -> str:
        """Sequential reasoning: Step-by-step analysis, assumption validation, and decision making"""
        return run_prompt_based_workflow("seq", query)

    # Ultra sequential reasoning
    @app.tool(name="sp_seq_ultra")
    def seq_ultra(query: str, persona: str = "seq_ultra") -> str:
        """Ultra sequential reasoning: Exhaustive analysis, multi-level reasoning, and optimization"""
        return run_prompt_based_workflow("seq_ultra", query)

    # Ultra compressed communication
    @app.tool(name="sp_ultracompressed")
    def ultracompressed(query: str, persona: str = "ultracompressed") -> str:
        """Ultra compressed communication: Maximum insight with minimum words, executive brevity"""
        return run_prompt_based_workflow("ultracompressed", query)

    # Trend analysis
    @app.tool(name="sp_wave")
    def wave(query: str, persona: str = "wave") -> str:
        """Trend analysis: Market analysis, forecasting, and strategic positioning"""
        return run_prompt_based_workflow("wave", query)

    # Service planning
    @app.tool(name="sp_service_planner")
    def service_planner(query: str, persona: str = "service_planner") -> str:
        """Service planning: Service design, customer journey, and implementation strategy"""
        return run_prompt_based_workflow("service_planner", query)

    # Troubleshooting
    @app.tool(name="sp_troubleshooting")
    def troubleshooting(query: str, persona: str = "troubleshooting") -> str:
        """Troubleshooting: Systematic problem diagnosis, root cause analysis, and resolution strategies"""
        return run_prompt_based_workflow("troubleshooting", query)

    # Documentation refactoring
    @app.tool(name="sp_docs_refector")
    def docs_refector(query: str, persona: str = "docs_refector") -> str:
        """Documentation refactoring: Content organization, consistency, and maintenance"""
        return run_prompt_based_workflow("docs_refector", query)

    # Abstention-first research analyst
    @app.tool(name="sp_resercher")
    def resercher(query: str, persona: str = "resercher") -> str:
        """Research synthesis with Self-RAG, Chain-of-Verification, and abstention discipline"""
        return run_prompt_based_workflow("resercher", query)

    # Confessional verification
    @app.tool(name="sp_double_check")
    def double_check(query: str, persona: str = "double_check") -> str:
        """Confessional integrity audit: Verify recent work, surface gaps, and request targeted follow-ups"""
        return run_prompt_based_workflow("double_check", query)

    # Mode management tools
    @app.tool(name="sp_gpt_mode_on")
    def gpt_mode_on() -> str:
        """Enable GPT mode for structured analysis and practical solutions"""
        try:
            import json
            import os

            mode_data = {"mode": "gpt", "timestamp": "2025-09-20T00:00:00Z"}
            mode_file = os.path.join(os.getcwd(), ".super-prompt", "mode.json")

            os.makedirs(os.path.dirname(mode_file), exist_ok=True)

            with open(mode_file, "w") as f:
                json.dump(mode_data, f, indent=2)

            return "✅ GPT mode activated. All personas will now use structured analysis."

        except Exception as e:
            return f"❌ Error activating GPT mode: {str(e)}"

    @app.tool(name="sp_grok_mode_on")
    def grok_mode_on() -> str:
        """Enable Grok mode for truth-seeking analysis and creative solutions"""
        try:
            import json
            import os

            mode_data = {"mode": "grok", "timestamp": "2025-09-20T00:00:00Z"}
            mode_file = os.path.join(os.getcwd(), ".super-prompt", "mode.json")

            os.makedirs(os.path.dirname(mode_file), exist_ok=True)

            with open(mode_file, "w") as f:
                json.dump(mode_data, f, indent=2)

            return "✅ Grok mode activated. All personas will now use truth-seeking analysis."

        except Exception as e:
            return f"❌ Error activating Grok mode: {str(e)}"

    @app.tool(name="sp_claude_mode_on")
    def claude_mode_on() -> str:
        """Enable Claude mode for structured, tag-driven prompt execution"""
        try:
            import json
            import os

            mode_data = {"mode": "claude", "timestamp": "2025-09-20T00:00:00Z"}
            mode_file = os.path.join(os.getcwd(), ".super-prompt", "mode.json")

            os.makedirs(os.path.dirname(mode_file), exist_ok=True)

            with open(mode_file, "w") as f:
                json.dump(mode_data, f, indent=2)

            return "✅ Claude mode activated. Personas will adopt Claude-native prompt structure and safety policies."

        except Exception as e:
            return f"❌ Error activating Claude mode: {str(e)}"

    @app.tool(name="sp_mode_get")
    def mode_get() -> str:
        """Get current LLM mode setting"""
        try:
            import json
            import os

            mode_file = os.path.join(os.getcwd(), ".super-prompt", "mode.json")
            if os.path.exists(mode_file):
                with open(mode_file, "r") as f:
                    mode_data = json.load(f)
                    mode = mode_data.get("mode", "gpt")
                    return f"Current mode: {mode.upper()}"
            else:
                return "Default mode: GPT"

        except Exception as e:
            return f"❌ Error reading mode: {str(e)}"

    @app.tool(name="sp_list_commands")
    def list_commands() -> str:
        """List all available Super Prompt commands and tools"""
        commands = [
            "sp_high - Strategic analysis and executive summaries",
            "sp_analyzer - Root cause analysis and systematic problem solving",
            "sp_architect - System architecture design and technical planning",
            "sp_backend - Backend development and API design",
            "sp_frontend - Frontend development and UI/UX design",
            "sp_dev - Full-stack development and implementation",
            "sp_security - Security analysis and threat modeling",
            "sp_performance - Performance optimization and monitoring",
            "sp_qa - Quality assurance and testing strategies",
            "sp_devops - DevOps engineering and infrastructure",
            "sp_refactorer - Code refactoring and quality improvement",
            "sp_doc_master - Documentation architecture and writing",
            "sp_db_expert - Database design and optimization",
            "sp_review - Code review and quality assessment",
            "sp_implement - Implementation planning and execution",
            "sp_mentor - Developer mentoring and skill development",
            "sp_scribe - Technical writing and documentation",
            "sp_debate - Strategic debate and critical analysis",
            "sp_optimize - Performance optimization and analysis",
            "sp_plan - Project planning and management",
            "sp_tasks - Task breakdown and management",
            "sp_specify - Requirements specification and analysis",
            "sp_seq - Sequential reasoning and step-by-step analysis",
            "sp_seq_ultra - Ultra-detailed sequential reasoning",
            "sp_ultracompressed - Maximum insight with minimum words",
            "sp_wave - Trend analysis and market forecasting",
            "sp_service_planner - Service design and customer experience",
            "sp_troubleshooting - Systematic problem diagnosis and resolution",
            "sp_docs_refector - Documentation organization and maintenance",
            "sp_resercher - Abstention-first research synthesis with evidence enforcement",
            "sp_double_check - Confessional integrity audit and follow-up requests",
            "sp_gpt_mode_on - Enable GPT mode for structured analysis",
            "sp_grok_mode_on - Enable Grok mode for creative analysis",
            "sp_claude_mode_on - Enable Claude mode for XML-structured, safety-focused response workflows",
            "sp_mode_get - Get current mode setting",
            "sp_list_commands - List all available commands"
        ]

        result = "🚀 **Super Prompt v5.0.5 - Available Commands:**\n\n"
        for cmd in commands:
            result += f"• {cmd}\n"

        result += "\n📝 **Usage:** Call any tool with a query parameter to get specialized analysis."
        return result

    return app
