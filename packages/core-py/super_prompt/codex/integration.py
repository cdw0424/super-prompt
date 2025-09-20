"""
Codex integration and assistance functions
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any
from textwrap import dedent

from ..paths import package_root, project_root

try:
    from importlib.metadata import version as _pkg_version
    _PACKAGE_VERSION = _pkg_version("super-prompt")
except Exception:
    _PACKAGE_VERSION = "dev"


# Codex persona briefs
CODEX_PERSONA_BRIEFS: Dict[str, str] = {
    "architect": dedent(
        """
        You are the Super Prompt Architect persona. Own system design decisions, surface trade-offs, and map work into phases before any coding begins.
        Your mission is to deliver a battle-tested architecture plan that other MCP tools can execute. Highlight modules, data flows, and risk mitigations.
        Suggest follow-up tools such as sp.plan, sp.tasks, sp.dev, and sp.review to continue execution.
        """
    ).strip(),
    "analyzer": dedent(
        """
        You are the Super Prompt Analyzer persona. Perform deep root-cause analysis, outline experiments, and identify telemetry needed to validate hypotheses.
        Deliver a prioritized diagnosis plan and recommend next MCP tools (e.g., sp.tasks for triage, sp.dev for fixes, sp.qa for validation).
        """
    ).strip(),
    "high": dedent(
        """
        You are the Super Prompt High-Effort strategist. Produce a comprehensive plan that balances architecture, delivery sequencing, and testing gates.
        Escalate to high reasoning automatically and hand off actionable steps to sp.plan, sp.tasks, and sp.dev.
        """
    ).strip(),
    "dev": dedent(
        """
        You are the Super Prompt Dev persona. Focus on minimal, testable diffs aligned with the existing codebase.
        Produce an implementation plan that references concrete files, guardrails, and validation steps. Recommend sp.tasks, sp.devops, or sp.review for follow-up.
        """
    ).strip(),
    "doc-master": dedent(
        """
        You are the Super Prompt Doc Master persona. Plan documentation architecture, contributors, and verification tactics.
        Deliver a doc plan that ties into sp.scribe, sp.qa, and sp.review for execution.
        """
    ).strip(),
}


def codex_env_overrides() -> Dict[str, str]:
    """Get allowed environment variables for Codex"""
    allowed = [
        "OPENAI_API_KEY",
        "OPENAI_KEY",
        "OPENAI_ORGANIZATION",
        "OPENAI_BASE_URL",
        "CODEX_API_KEY",
        "CODEX_HOME",
        "RUST_LOG",
    ]
    env: Dict[str, str] = {}
    for key in allowed:
        value = os.environ.get(key)
        if value:
            env[key] = value
    return env


def codex_persona_key(tool_name: str) -> str:
    """Get persona key from tool name"""
    return tool_name or "general"


def codex_persona_brief(persona_key: str) -> str:
    """Get persona brief for Codex"""
    default_brief = dedent(
        """
        You are part of the Super Prompt multi-agent workflow. Produce a numbered implementation plan first,
        call out risks, and recommend which MCP tools should run next (e.g., sp.plan, sp.tasks, sp.dev, sp.review).
        """
    ).strip()
    return CODEX_PERSONA_BRIEFS.get(persona_key, default_brief)


def build_codex_prompt(query: str, context: str, persona_key: str) -> tuple[str, str]:
    """Build prompt for Codex interaction"""
    brief = codex_persona_brief(persona_key)
    context_block = (context or "").strip()
    if len(context_block) > 1200:
        context_block = context_block[:1200] + "..."

    base_instructions = dedent(
        f"""
        {brief}

        Operate in plan-first mode. Your response MUST contain two sections:
        PLAN: Numbered steps with clear owners, file targets, and validation gates.
        TOOLS: Bullet list mapping Super Prompt MCP commands to next actions (e.g., sp.plan, sp.tasks, sp.dev, sp.review, sp.qa).

        Reference concrete files or directories whenever possible and identify risks or unknowns that require further discovery.
        """
    ).strip()

    prompt = dedent(
        f"""
        {base_instructions}

        [USER REQUEST]
        {query.strip() or 'No user request provided.'}

        [PROJECT INSIGHTS]
        {context_block or 'No additional project context provided.'}

        Respond with actionable guidance that other MCP tools can execute without additional clarification.
        """
    ).strip()

    return prompt, base_instructions


def call_codex_assistance_mcp(query: str, context: str, tool_name: str) -> str:
    """Call Codex assistance via MCP bridge"""
    persona_key = codex_persona_key(tool_name)
    prompt, base_instructions = build_codex_prompt(query, context, persona_key)

    payload = {
        "prompt": prompt,
        "model": "gpt-5-codex",
        "includePlan": True,
        "baseInstructions": base_instructions,
        "arguments": {},
        "env": codex_env_overrides(),
        "cwd": str(project_root()),
        "clientName": "super-prompt",
        "clientVersion": _PACKAGE_VERSION,
        "reasoningEffort": "high",
        "timeoutMs": 180000,
    }

    bridge = package_root() / "src" / "tools" / "codex-mcp.js"
    if not bridge.exists():
        raise FileNotFoundError(f"codex MCP bridge missing at {bridge}")

    env = os.environ.copy()
    env["CODEX_MCP_PAYLOAD"] = json.dumps(payload)

    cmd = ["node", str(bridge)]
    print(f"-------- codex: MCP bridge invoking ({persona_key})", file=sys.stderr, flush=True)
    completed = subprocess.run(
        cmd,
        capture_output=False,  # MCP stdout safety: do not capture stdout
        stdout=subprocess.DEVNULL,  # Redirect stdout to /dev/null
        stderr=subprocess.PIPE,  # Capture stderr for error handling
        text=True,
        env=env,
        timeout=payload["timeoutMs"] / 1000,
    )

    stderr = completed.stderr.strip()
    if stderr:
        last_line = stderr.splitlines()[-1]
        try:
            parsed = json.loads(last_line)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"Invalid JSON from codex MCP bridge: {error}: {last_line}")

        if not parsed.get("ok"):
            raise RuntimeError(parsed.get("text") or "Codex MCP returned an error")

        text = (parsed.get("text") or "").strip()
        if text:
            return text

        structured = parsed.get("structuredContent")
        if structured:
            return json.dumps(structured)

        content = parsed.get("content")
        if content:
            return json.dumps(content)

        return "Codex MCP returned no textual content"

    stderr = completed.stderr.strip()
    raise RuntimeError(stderr or "Codex MCP produced no output")


def call_codex_assistance_cli(query: str, context: str, tool_name: str) -> str:
    """Call Codex assistance via CLI fallback"""
    situation_summary = summarize_situation_for_codex(query, context, tool_name)

    mcp_servers_config = "{}"
    codex_cmd = [
        "codex",
        "exec",
        "-c",
        f"mcp_servers={mcp_servers_config}",
        "-c",
        'model_reasoning_effort="high"',
        "--",
        situation_summary,
    ]

    result = subprocess.run(
        codex_cmd,
        capture_output=False,  # MCP stdout safety: do not capture stdout
        stdout=subprocess.DEVNULL,  # Redirect stdout to /dev/null
        stderr=subprocess.PIPE,  # Capture stderr for result
        text=True,
        timeout=90,
    )

    if result.returncode == 0:
        return result.stderr.strip()  # Use stderr instead of stdout

    error_msg = result.stderr.strip() or "Codex CLI error"
    return f"Codex assistance unavailable: {error_msg}"


def call_codex_assistance(query: str, context: str = "", tool_name: str = "general") -> str:
    """Route Codex assistance using the MCP bridge with CLI fallback."""
    try:
        return call_codex_assistance_mcp(query, context, tool_name)
    except FileNotFoundError as missing:
        print(
            f"-------- codex: MCP bridge missing ({missing}); falling back to CLI",
            file=sys.stderr,
            flush=True,
        )
    except subprocess.TimeoutExpired as timeout_err:
        print(
            f"-------- codex: MCP bridge timeout ({tool_name}): {timeout_err}",
            file=sys.stderr,
            flush=True,
        )
    except Exception as error:
        print(
            f"-------- codex: MCP bridge failure ({tool_name}): {error}",
            file=sys.stderr,
            flush=True,
        )

    return call_codex_assistance_cli(query, context, tool_name)


def summarize_situation_for_codex(
    query: str, context: str = "", tool_name: str = "general"
) -> str:
    """Create concise situation summary and key question for Codex"""
    # Use different prompt strategies per tool
    if tool_name == "high":
        prompt = f"""You are a strategic reasoning expert. Analyze this situation and provide the most critical strategic insight needed:

Situation: {context[:300]}...
Query: {query}

Provide ONLY the most important strategic recommendation or insight needed to solve this problem. Be concise but comprehensive."""
    elif tool_name in ["architect", "dev", "backend", "frontend"]:
        prompt = f"""You are a senior {tool_name} engineer. Provide expert technical guidance:

Context: {context[:250]}...
Task: {query}

What is the ONE most critical technical insight or recommendation for this implementation? Focus on best practices and potential issues."""
    elif tool_name in ["analyzer", "qa", "security"]:
        prompt = f"""You are a {tool_name} specialist. Provide critical analysis:

Context: {context[:250]}...
Issue: {query}

What is the primary risk or key insight that must be addressed first? Be specific and actionable."""
    else:
        prompt = f"""Expert analysis needed:

Context: {context[:250]}...
Query: {query}

What is the most important insight or recommendation for this situation? Focus on the core issue."""

    return prompt[:600]  # Consider Codex input limits


def should_use_codex_assistance(query: str, tool_name: str) -> bool:
    """Determine if Codex assistance is needed for logical reasoning"""
    mandatory = {
        "architect",
        "frontend",
        "backend",
        "security",
        "performance",
        "analyzer",
        "qa",
        "refactorer",
        "devops",
        "mentor",
        "scribe",
        "dev",
        "doc-master",
        "high",
    }
    if tool_name in mandatory:
        return True

    # Use Codex for complex queries
    complexity_indicators = [
        "analyze",
        "optimize",
        "design",
        "architecture",
        "strategy",
        "complex",
        "challenging",
        "difficult",
        "problem",
        "issue",
        "how to",
        "why",
        "what if",
        "consider",
        "evaluate",
        "architect",
        "implement",
        "plan",
        "review",
        "debug",
        "troubleshoot",
        "investigate",
        "research",
        "explore",
    ]

    query_lower = query.lower()
    has_complexity = any(indicator in query_lower for indicator in complexity_indicators)

    # For long queries (high probability of needing logical reasoning)
    is_long_query = len(query.split()) > 15

    # Contains code or technical content
    has_technical_content = any(
        keyword in query_lower
        for keyword in [
            "code",
            "function",
            "class",
            "api",
            "database",
            "sql",
            "javascript",
            "python",
            "react",
            "node",
            "server",
        ]
    )

    return has_complexity or is_long_query or has_technical_content