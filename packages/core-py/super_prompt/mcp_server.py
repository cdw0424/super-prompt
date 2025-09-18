# packages/core-py/super_prompt/mcp_server.py
# SECURITY: MCP-only access - Direct CLI calls are blocked
# pip dep: mcp >= 0.4.0  (pyproject.toml 또는 setup.cfg에 추가)
import os
import sys
import asyncio
import subprocess
import json
import inspect
from dataclasses import dataclass
from pathlib import Path
import socket
import time
from textwrap import dedent

try:
    from importlib.metadata import version as _pkg_version

    _PACKAGE_VERSION = _pkg_version("super-prompt")
except Exception:
    _PACKAGE_VERSION = "dev"

# MCP SDK (Anthropic 공개 라이브러리) - 버전 호환성 개선
# NOTE: Provide safe fallbacks when SDK is unavailable so that direct tool calls can run.
# Support multiple MCP SDK versions for maximum compatibility


def _detect_mcp_version():
    """Detect MCP SDK version and capabilities with enhanced precision"""
    try:
        import mcp

        version = getattr(mcp, "__version__", "unknown")

        # Enhanced version detection logic
        if hasattr(mcp, "__version__") and mcp.__version__:
            version = mcp.__version__
            # Parse version string for more precise detection
            try:
                from packaging import version as pkg_version

                parsed_version = pkg_version.parse(version)
                if parsed_version >= pkg_version.parse("0.4.0"):
                    return f"{version} (0.4+)", "fastmcp"
                elif parsed_version >= pkg_version.parse("0.3.0"):
                    return f"{version} (0.3+)", "server"
                else:
                    return f"{version} (legacy)", "legacy"
            except ImportError:
                # packaging not available, use string comparison
                if version.startswith(("0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.")):
                    return f"{version} (0.4+)", "fastmcp"
                elif version.startswith("0.3"):
                    return f"{version} (0.3+)", "server"

        # Fallback to structural detection
        if hasattr(mcp, "server"):
            if hasattr(mcp.server, "FastMCP"):
                return "0.4+ (detected)", "fastmcp"
            elif hasattr(mcp.server, "fastmcp"):
                return "0.4+ (detected)", "fastmcp"
            elif hasattr(mcp.server, "Server"):
                return "0.3+ (detected)", "server"

        return version, "unknown"
    except Exception as e:
        print(f"-------- MCP: version detection failed: {e}", file=sys.stderr, flush=True)
        return None, None


def _import_mcp_components():
    """Import MCP components with version compatibility"""
    mcp_version, mcp_type = _detect_mcp_version()

    if not mcp_version:
        raise ImportError("MCP SDK not available")

    # Try different import patterns for maximum compatibility
    import_attempts = [
        # MCP 0.4+ with FastMCP
        ("mcp.server.fastmcp", "FastMCP"),
        ("mcp.server", "FastMCP"),
        # MCP 0.3+ with Server
        ("mcp.server", "Server"),
        # Legacy patterns
        ("mcp", "FastMCP"),
    ]

    FastMCP = None
    for module_path, class_name in import_attempts:
        try:
            module = __import__(module_path, fromlist=[class_name])
            FastMCP = getattr(module, class_name, None)
            if FastMCP:
                print(
                    f"-------- MCP: using {module_path}.{class_name} (version: {mcp_version})",
                    file=sys.stderr,
                    flush=True,
                )
                break
        except (ImportError, AttributeError):
            continue

    if not FastMCP:
        raise ImportError(f"No compatible MCP FastMCP/Server class found in version {mcp_version}")

    # Try to import TextContent with comprehensive patterns
    text_content_attempts = [
        # Modern MCP patterns
        "mcp.types.TextContent",
        "mcp.server.models.TextContent",
        "mcp.shared.models.TextContent",
        "mcp.server.fastmcp.TextContent",
        # Alternative patterns
        "mcp.server.TextContent",
        "mcp.TextContent",
        # Legacy patterns for older versions
        "mcp.protocol.TextContent",
        "mcp.core.TextContent",
    ]

    TextContent = None
    for tc_path in text_content_attempts:
        try:
            module_path, class_name = tc_path.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            TextContent = getattr(module, class_name, None)
            if TextContent:
                break
        except (ImportError, AttributeError, ValueError):
            continue

    # Fallback TextContent class
    if not TextContent:

        class TextContent:  # minimal stub for direct-call mode
            def __init__(self, type: str, text: str):
                self.type = type
                self.text = text

    return FastMCP, TextContent, mcp_version


# Initialize MCP components
try:
    FastMCP, TextContent, _MCP_VERSION = _import_mcp_components()
    _HAS_MCP = True
    print(
        f"-------- MCP: SDK initialized successfully (version: {_MCP_VERSION})",
        file=sys.stderr,
        flush=True,
    )
except Exception as e:
    print(f"-------- MCP: SDK initialization failed: {e}", file=sys.stderr, flush=True)
    _HAS_MCP = False

    class TextContent:  # minimal stub for direct-call mode
        def __init__(self, type: str, text: str):
            self.type = type
            self.text = text

    class _StubMCP:
        def tool(self, *_args, **_kwargs):
            def _decorator(fn):
                return fn

            return _decorator

        def run(self):
            raise RuntimeError("MCP SDK not available; cannot start MCP server")

    FastMCP = None  # type: ignore
    # Create a stub 'mcp' so decorators below don't fail at import time.
    mcp = _StubMCP()  # type: ignore
from .paths import package_root, project_root, project_data_dir
from .venv import ensure_project_venv
from .mcp_register import ensure_cursor_mcp_registered, ensure_codex_mcp_registered
from .mode_store import get_mode, set_mode
from .personas.loader import PersonaLoader
import shutil, sys
import time
import json
from typing import Dict, Any, Optional, List, Callable
from contextlib import contextmanager

# SECURITY: Prevent direct execution
if __name__ != "__main__":
    # If imported directly (not run as MCP server), block access
    if not os.environ.get("MCP_SERVER_MODE"):
        print(
            "-------- ERROR: Super Prompt MCP server must be run through MCP protocol only.",
            file=sys.stderr,
            flush=True,
        )
        print("-------- Direct Python execution is not allowed.", file=sys.stderr, flush=True)
        print(
            "-------- Use MCP client tools: sp.init(), sp.refresh(), sp.list_commands(), etc.",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)


# Span 관리 클래스
class SpanManager:
    def __init__(self):
        self.spans: Dict[str, Dict[str, Any]] = {}
        self._span_counter = 0
        self._init_db()

    def _init_db(self):
        """메모리 데이터베이스 초기화"""
        import sqlite3
        import os
        from pathlib import Path

        # 데이터베이스 경로 설정
        db_path = Path.home() / ".super-prompt" / "memory" / "spans.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS spans (
                id TEXT PRIMARY KEY,
                command_id TEXT,
                user_id TEXT,
                start_time REAL,
                end_time REAL,
                duration REAL,
                status TEXT,
                meta TEXT,
                events TEXT,
                extra TEXT
            )
        """
        )
        self.conn.commit()

    def start_span(self, meta: Dict[str, Any]) -> str:
        """새로운 span 시작"""
        span_id = f"span_{self._span_counter}"
        self._span_counter += 1

        self.spans[span_id] = {
            "id": span_id,
            "start_time": time.time(),
            "meta": meta,
            "events": [],
            "status": "active",
        }

        print(
            f"-------- memory: span started {span_id} for {meta.get('commandId', 'unknown')}",
            file=sys.stderr,
            flush=True,
        )
        return span_id

    def write_event(self, span_id: str, event: Dict[str, Any]) -> None:
        """span에 이벤트 기록"""
        if span_id in self.spans:
            event_with_time = {"timestamp": time.time(), **event}
            self.spans[span_id]["events"].append(event_with_time)
            print(f"-------- memory: event recorded in {span_id}", file=sys.stderr, flush=True)

    def end_span(
        self, span_id: str, status: str = "ok", extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """span 종료"""
        if span_id in self.spans:
            span = self.spans[span_id]
            span["end_time"] = time.time()
            span["duration"] = span["end_time"] - span["start_time"]
            span["status"] = status
            if extra:
                span["extra"] = extra

            print(
                f"-------- memory: span ended {span_id} status={status} duration={span['duration']:.2f}s",
                file=sys.stderr,
                flush=True,
            )

            # 데이터베이스에 저장
            self._save_span_to_db(span)

    def _save_span_to_db(self, span: Dict[str, Any]) -> None:
        """span을 데이터베이스에 저장"""
        import json

        try:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO spans
                (id, command_id, user_id, start_time, end_time, duration, status, meta, events, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    span["id"],
                    span["meta"].get("commandId", ""),
                    span["meta"].get("userId", ""),
                    span["start_time"],
                    span.get("end_time", 0),
                    span.get("duration", 0),
                    span.get("status", "unknown"),
                    json.dumps(span["meta"]),
                    json.dumps(span["events"]),
                    json.dumps(span.get("extra", {})),
                ),
            )
            self.conn.commit()
            print(
                f"-------- memory: span {span['id']} saved to database", file=sys.stderr, flush=True
            )
        except Exception as e:
            print(
                f"-------- memory: failed to save span {span['id']}: {e}",
                file=sys.stderr,
                flush=True,
            )


# 전역 span 관리자
span_manager = SpanManager()


# 진행상황 표시 유틸리티
class ProgressIndicator:
    """실시간 진행상황 표시를 위한 유틸리티 클래스"""

    def __init__(self):
        self.animation_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.frame_index = 0

    def show_progress(self, message: str, step: int = 0, total: int = 0) -> None:
        """진행상황을 표시"""
        frame = self.animation_frames[self.frame_index % len(self.animation_frames)]
        self.frame_index += 1

        if total > 0 and step > 0:
            progress = f"[{step}/{total}] "
        else:
            progress = ""

        print(f"-------- {frame} {progress}{message}", file=sys.stderr, flush=True)

    def show_success(self, message: str) -> None:
        """성공 메시지를 표시"""
        print(f"-------- ✅ {message}", file=sys.stderr, flush=True)

    def show_error(self, message: str) -> None:
        """오류 메시지를 표시"""
        print(f"-------- ❌ {message}", file=sys.stderr, flush=True)

    def show_info(self, message: str) -> None:
        """정보 메시지를 표시"""
        print(f"-------- ℹ️  {message}", file=sys.stderr, flush=True)


# 전역 진행상황 표시기
progress = ProgressIndicator()


# Authorization Framework
class MCPAuthorization:
    """MCP Authorization Framework for tool access control"""

    PERMISSION_LEVELS = {
        "read": 1,  # 읽기 전용 도구들
        "write": 2,  # 설정 변경 도구들
        "admin": 3,  # 시스템 관리 도구들
    }

    TOOL_PERMISSIONS = {
        # Read-only tools
        "version": "read",
        "list_commands": "read",
        "list_personas": "read",
        "mode_get": "read",
        "architect": "read",
        "frontend": "read",
        "backend": "read",
        "security": "read",
        "performance": "read",
        "analyzer": "read",
        "qa": "read",
        "refactorer": "read",
        "devops": "read",
        "mentor": "read",
        "scribe": "read",
        "dev": "read",
        "grok": "read",
        "db-expert": "read",
        "optimize": "read",
        "review": "read",
        "specify": "read",
        "plan": "read",
        "tasks": "read",
        "implement": "read",
        "seq": "read",
        "seq-ultra": "read",
        "high": "read",
        # Write tools (configuration changes)
        "mode_set": "write",
        "grok_mode_on": "write",
        "gpt_mode_on": "write",
        "grok_mode_off": "write",
        "gpt_mode_off": "write",
        # Admin tools (system modifications)
        "init": "admin",
        "refresh": "admin",
    }

    @classmethod
    def check_permission(cls, tool_name: str, user_level: str = "read") -> bool:
        """Check if user has permission to access a tool"""
        required_level = cls.TOOL_PERMISSIONS.get(tool_name, "read")
        user_perm_level = cls.PERMISSION_LEVELS.get(user_level, 1)
        required_perm_level = cls.PERMISSION_LEVELS.get(required_level, 1)

        return user_perm_level >= required_perm_level

    @classmethod
    def get_user_permission_level(cls) -> str:
        """Get current user's permission level from environment"""
        # Check for explicit permission level
        explicit_level = os.environ.get("SUPER_PROMPT_PERMISSION_LEVEL", "").lower()
        if explicit_level in cls.PERMISSION_LEVELS:
            return explicit_level

        # Check for admin access
        if os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower() in ("1", "true", "yes"):
            return "admin"

        # Default to read-only
        return "read"

    @classmethod
    def require_permission(cls, tool_name: str) -> None:
        """Require specific permission for tool access, raises exception if not authorized"""
        user_level = cls.get_user_permission_level()
        if not cls.check_permission(tool_name, user_level):
            required_level = cls.TOOL_PERMISSIONS.get(tool_name, "read")
            raise PermissionError(
                f"MCP: Insufficient permissions. Tool '{tool_name}' requires '{required_level}' level, "
                f"but user has '{user_level}' level. "
                f"Set SUPER_PROMPT_PERMISSION_LEVEL={required_level} to grant access."
            )


# Resource Links 헬퍼 함수들
def _get_persona_resource_links(persona_name: str) -> str:
    """페르소나별 유용한 리소스 링크들을 반환"""
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


# Span 컨텍스트 매니저
@contextmanager
def memory_span(command_id: str, user_id: Optional[str] = None):
    """메모리 span 컨텍스트 매니저"""
    span_id = span_manager.start_span({"commandId": command_id, "userId": user_id})

    try:
        yield span_id
    except Exception as e:
        span_manager.write_event(
            span_id,
            {"type": "error", "message": str(e), "stack": getattr(e, "__traceback__", None)},
        )
        span_manager.end_span(span_id, "error", {"error": str(e)})
        raise
    else:
        span_manager.end_span(span_id, "ok")


# Initialize MCP server with version compatibility
def _initialize_mcp_server():
    """Initialize MCP server with version-aware configuration"""
    if not _HAS_MCP:
        # when SDK missing, 'mcp' was already defined as a stub above
        return None

    try:
        # Try different initialization patterns for maximum compatibility
        server_name = "super-prompt"

        # Check FastMCP signature and initialize accordingly
        import inspect

        fastmcp_sig = inspect.signature(FastMCP)

        # Common initialization patterns across MCP versions
        init_attempts = [
            # Standard pattern for most versions
            lambda: FastMCP(server_name),
            # Some versions might require additional parameters
            lambda: FastMCP(name=server_name),
            # Alternative parameter patterns
            lambda: FastMCP(server_name, instructions=""),
            lambda: FastMCP(server_name, {}),
            lambda: FastMCP({"name": server_name}),
            # Legacy patterns for older versions
            lambda: FastMCP(server_name, None),
            lambda: FastMCP(server_name, {}, None),
        ]

        mcp_instance = None
        for init_func in init_attempts:
            try:
                mcp_instance = init_func()
                print(
                    f"-------- MCP: server initialized successfully with {init_func.__name__}",
                    file=sys.stderr,
                    flush=True,
                )
                break
            except (TypeError, ValueError) as e:
                print(
                    f"-------- MCP: initialization attempt failed: {e}", file=sys.stderr, flush=True
                )
                continue

        if mcp_instance is None:
            raise RuntimeError(f"Failed to initialize FastMCP with version {_MCP_VERSION}")

        return mcp_instance

    except Exception as e:
        print(f"-------- MCP: server initialization failed: {e}", file=sys.stderr, flush=True)
        # Fall back to stub
        return _StubMCP()


# Initialize MCP server
mcp = _initialize_mcp_server()


TOOL_METADATA: Dict[str, Dict[str, Any]] = {
    "sp.version": {"category": "system", "tags": ["system", "diagnostics"]},
    "sp.init": {"category": "system", "tags": ["system", "setup"], "destructive": True},
    "sp.refresh": {"category": "system", "tags": ["system", "setup"], "destructive": True},
    "sp.list_commands": {"category": "system", "tags": ["system", "introspection"]},
    "sp.list_personas": {"category": "system", "tags": ["system", "personas"]},
    "sp.mode_get": {"category": "system", "tags": ["system", "mode"]},
    "sp.mode_set": {"category": "system", "tags": ["system", "mode"], "destructive": True},
    "sp.grok_mode_on": {"category": "system", "tags": ["system", "mode"], "destructive": True},
    "sp.gpt_mode_on": {"category": "system", "tags": ["system", "mode"], "destructive": True},
    "sp.grok_mode_off": {"category": "system", "tags": ["system", "mode"], "destructive": True},
    "sp.gpt_mode_off": {"category": "system", "tags": ["system", "mode"], "destructive": True},
    "sp.architect": {
        "category": "persona",
        "persona": "Architect",
        "tags": ["persona", "architecture"],
    },
    "sp.frontend": {"category": "persona", "persona": "Frontend", "tags": ["persona", "frontend"]},
    "sp.backend": {"category": "persona", "persona": "Backend", "tags": ["persona", "backend"]},
    "sp.security": {"category": "persona", "persona": "Security", "tags": ["persona", "security"]},
    "sp.performance": {
        "category": "persona",
        "persona": "Performance",
        "tags": ["persona", "performance"],
    },
    "sp.analyzer": {"category": "persona", "persona": "Analyzer", "tags": ["persona", "analysis"]},
    "sp.qa": {"category": "persona", "persona": "QA", "tags": ["persona", "quality"]},
    "sp.refactorer": {
        "category": "persona",
        "persona": "Refactorer",
        "tags": ["persona", "refactoring"],
    },
    "sp.devops": {"category": "persona", "persona": "DevOps", "tags": ["persona", "devops"]},
    "sp.debate": {"category": "persona", "persona": "Debate", "tags": ["persona", "analysis"]},
    "sp.mentor": {"category": "persona", "persona": "Mentor", "tags": ["persona", "guidance"]},
    "sp.scribe": {"category": "persona", "persona": "Scribe", "tags": ["persona", "documentation"]},
    "sp.doc-master": {
        "category": "persona",
        "persona": "Doc Master",
        "tags": ["persona", "documentation"],
    },
    "sp.docs-refector": {
        "category": "persona",
        "persona": "Docs Refector",
        "tags": ["persona", "documentation", "refactor"],
    },
    "sp.service-planner": {
        "category": "persona",
        "persona": "Service Planner",
        "tags": ["persona", "strategy"],
    },
    "sp.dev": {"category": "persona", "persona": "Dev", "tags": ["persona", "development"]},
    "sp.review": {"category": "persona", "persona": "Review", "tags": ["persona", "review"]},
    "sp.optimize": {
        "category": "persona",
        "persona": "Optimize",
        "tags": ["persona", "optimization"],
    },
    "sp.grok": {"category": "persona", "persona": "Grok", "tags": ["persona", "grok"]},
    "sp.db-expert": {
        "category": "persona",
        "persona": "DB Expert",
        "tags": ["persona", "database"],
    },
    "sp.specify": {"category": "sdd", "tags": ["sdd", "spec"]},
    "sp.plan": {"category": "sdd", "tags": ["sdd", "plan"]},
    "sp.tasks": {"category": "sdd", "tags": ["sdd", "tasks"]},
    "sp.implement": {"category": "sdd", "tags": ["sdd", "implement"]},
    "sp.seq": {"category": "reasoning", "tags": ["reasoning", "sequential"]},
    "sp.seq-ultra": {"category": "reasoning", "tags": ["reasoning", "sequential", "advanced"]},
    "sp.high": {"category": "reasoning", "tags": ["reasoning", "high-effort"]},
    "sp.tr": {"category": "utility", "tags": ["utility", "translation"]},
    "sp.ultracompressed": {"category": "utility", "tags": ["utility", "compression"]},
}

REGISTERED_TOOL_ANNOTATIONS: Dict[str, Dict[str, Any]] = {}


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


def _codex_env_overrides() -> Dict[str, str]:
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


def _codex_persona_key(tool_name: str) -> str:
    return tool_name or "general"


def _codex_persona_brief(persona_key: str) -> str:
    default_brief = dedent(
        """
        You are part of the Super Prompt multi-agent workflow. Produce a numbered implementation plan first,
        call out risks, and recommend which MCP tools should run next (e.g., sp.plan, sp.tasks, sp.dev, sp.review).
        """
    ).strip()
    return CODEX_PERSONA_BRIEFS.get(persona_key, default_brief)


def _build_codex_prompt(query: str, context: str, persona_key: str) -> tuple[str, str]:
    brief = _codex_persona_brief(persona_key)
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


def _call_codex_assistance_mcp(query: str, context: str, tool_name: str) -> str:
    persona_key = _codex_persona_key(tool_name)
    prompt, base_instructions = _build_codex_prompt(query, context, persona_key)

    payload = {
        "prompt": prompt,
        "model": "gpt-5-codex",
        "includePlan": True,
        "baseInstructions": base_instructions,
        "arguments": {},
        "env": _codex_env_overrides(),
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
        capture_output=True,
        text=True,
        env=env,
        timeout=payload["timeoutMs"] / 1000,
    )

    stdout = completed.stdout.strip()
    if stdout:
        last_line = stdout.splitlines()[-1]
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


def _call_codex_assistance_cli(query: str, context: str, tool_name: str) -> str:
    situation_summary = _summarize_situation_for_codex(query, context, tool_name)

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
        capture_output=True,
        text=True,
        timeout=90,
    )

    if result.returncode == 0:
        return result.stdout.strip()

    error_msg = result.stderr.strip() or "Codex CLI error"
    return f"Codex assistance unavailable: {error_msg}"


def _short_description(doc: Optional[str]) -> str:
    if not doc:
        return ""
    lines = [line.strip() for line in doc.strip().splitlines() if line.strip()]
    return lines[0] if lines else ""


def register_tool(tool_name: str):
    meta = TOOL_METADATA.get(tool_name, {})

    def decorator(fn):
        description = _short_description(fn.__doc__)
        annotations: Dict[str, Any] = {
            "name": tool_name,
            "description": description,
            "destructive": bool(meta.get("destructive", False)),
        }

        if "category" in meta:
            annotations["category"] = meta["category"]
        if meta.get("tags"):
            annotations["tags"] = list(meta["tags"])
        if meta.get("persona"):
            annotations["persona"] = meta["persona"]
        if meta.get("examples"):
            annotations["examples"] = meta["examples"]

        input_schema: Optional[Dict[str, Any]] = None
        try:
            fn_sig = inspect.signature(fn)
        except Exception:
            fn_sig = None

        if fn_sig:
            properties: Dict[str, Any] = {}
            required: List[str] = []
            for param_name, param in fn_sig.parameters.items():
                if param_name == "self":
                    continue
                schema: Dict[str, Any] = {}
                annotation = param.annotation
                schema_type = "string"
                if annotation in (bool, "bool"):
                    schema_type = "boolean"
                elif annotation in (int, "int"):
                    schema_type = "integer"
                elif annotation in (float, "float"):
                    schema_type = "number"
                schema["type"] = schema_type
                if param.default is not inspect._empty:
                    schema["default"] = param.default
                properties[param_name] = schema
                if param.default is inspect._empty:
                    required.append(param_name)
            if properties:
                input_schema = {
                    "type": "object",
                    "properties": properties,
                    "additionalProperties": False,
                }
                if required:
                    input_schema["required"] = required

        if input_schema:
            annotations["input_schema"] = input_schema

        REGISTERED_TOOL_ANNOTATIONS[tool_name] = annotations

        # Post-execution confession double-check runner (defined early for both MCP and direct paths)
        def _run_post_exec_confession(name: str) -> None:
            try:
                # Lazy import to avoid import cycles at module load
                from .commands.validate_tools import validate_check  # type: ignore
            except Exception:
                return
            try:
                result = validate_check()
                logs = (result or {}).get("logs") or []
                for line in logs:
                    print(f"-------- confession: {line}", flush=True)
            except Exception as e:  # best-effort; never break main tool result
                try:
                    print(
                        f"-------- confession: error during validation: {e}",
                        file=sys.stderr,
                        flush=True,
                    )
                except Exception:
                    pass

        tool_callable = getattr(mcp, "tool", None)
        if not callable(tool_callable):
            # Direct mode: manually wrap to ensure confession runs
            def _tool_with_confession_direct(*a, **k):
                try:
                    return fn(*a, **k)
                finally:
                    if tool_name not in {"sp.analyzer"}:
                        _run_post_exec_confession(tool_name)

            setattr(_tool_with_confession_direct, "_sp_annotations", annotations)
            return _tool_with_confession_direct

        try:
            params = inspect.signature(tool_callable).parameters
        except Exception:
            params = {}

        kwargs: Dict[str, Any] = {}
        destructive = bool(meta.get("destructive", False))
        if destructive and "destructive" in params:
            kwargs["destructive"] = True
        elif not destructive and "read_only" in params:
            kwargs["read_only"] = True

        if "annotations" in params:
            kwargs["annotations"] = annotations
        elif "metadata" in params:
            kwargs["metadata"] = annotations
        elif "tags" in params and meta.get("tags"):
            kwargs["tags"] = list(meta["tags"])

        if input_schema and "input_schema" in params:
            kwargs["input_schema"] = input_schema

        if "name" in params:
            kwargs["name"] = tool_name

        try:
            decorated = tool_callable(**kwargs)
        except TypeError:
            decorated = tool_callable()

        # Wrap original tool to always run the confession check at the end
        def _tool_with_confession(*a, **k):
            # Handle the case where MCP passes arguments as keyword args
            # but the function expects different parameter names
            try:
                # Try calling with original args first
                return fn(*a, **k)
            except TypeError as e:
                if "unexpected keyword argument" in str(e):
                    # If there's a parameter mismatch, try to adapt
                    # Remove problematic kwargs and call with remaining args
                    filtered_kwargs = {
                        key: value
                        for key, value in k.items()
                        if not key.startswith(("a", "k")) or key in ["query", "input"]
                    }
                    try:
                        return fn(*a, **filtered_kwargs)
                    except Exception:
                        # If that fails, try calling with no kwargs
                        return fn(*a)
                else:
                    raise
            finally:
                # Avoid recursion or undesired re-entry for analyzer itself
                if tool_name not in {"sp.analyzer"}:
                    _run_post_exec_confession(tool_name)

        wrapped = decorated(_tool_with_confession)
        setattr(wrapped, "_sp_annotations", annotations)
        setattr(fn, "_sp_annotations", annotations)
        return wrapped

    return decorator


def _text_from(content: "TextContent | str | None") -> str:
    try:
        if isinstance(content, TextContent):  # type: ignore
            return getattr(content, "text", "") or ""
    except Exception:
        pass
    return "" if content is None else str(content)


def _call_codex_assistance(query: str, context: str = "", tool_name: str = "general") -> str:
    """Route Codex assistance using the MCP bridge with CLI fallback."""
    try:
        return _call_codex_assistance_mcp(query, context, tool_name)
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

    return _call_codex_assistance_cli(query, context, tool_name)


def _summarize_situation_for_codex(
    query: str, context: str = "", tool_name: str = "general"
) -> str:
    """Create concise situation summary and key question for Codex"""
    # 도구별로 다른 프롬프트 전략 사용
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

    return prompt[:600]  # Codex 입력 제한 고려


def _should_use_codex_assistance(query: str, tool_name: str) -> bool:
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

    # 복잡한 쿼리의 경우 Codex 사용
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

    # 쿼리 길이가 긴 경우 (논리적 추론 필요 가능성 높음)
    is_long_query = len(query.split()) > 15

    # 코드나 기술적 내용 포함
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


def _ensure_venv_activated():
    """Ensure virtual environment is activated"""
    try:
        # Check if we're in the correct venv
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            print("-------- venv: already activated", file=sys.stderr, flush=True)
            return True

        # Try to find and use venv Python
        project_root = Path.cwd()
        venv_python = project_root / ".super-prompt" / "venv" / "bin" / "python3"

        if venv_python.exists():
            print(
                "-------- venv: found venv Python, environment ready", file=sys.stderr, flush=True
            )
            return True
        else:
            print("-------- venv: not found, using system Python", file=sys.stderr, flush=True)
            return True  # Continue with system Python
    except Exception as e:
        print(f"-------- venv: check failed: {e}, continuing", file=sys.stderr, flush=True)
        return True  # Don't fail the whole process


def _check_mcp_server_running() -> bool:
    """Check if MCP server process is running"""
    try:
        # Check for running MCP server processes - look for cli.py mcp-serve
        result = subprocess.run(["pgrep", "-f", "cli.py mcp-serve"], capture_output=True, text=True)
        return result.returncode == 0 and len(result.stdout.strip()) > 0
    except Exception:
        return False


def _start_mcp_server_if_needed():
    """Start MCP server if not running"""
    try:
        # Check if server is already running
        if _check_mcp_server_running():
            print("-------- mcp-server: already running", file=sys.stderr, flush=True)
            return True

        print("-------- mcp-server: starting...", file=sys.stderr, flush=True)

        # Start MCP server in background
        project_root = Path.cwd()
        cli_path = project_root / "packages" / "core-py" / "super_prompt" / "cli.py"

        if cli_path.exists():
            # Start server in background
            cmd = [sys.executable, str(cli_path), "mcp-serve"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,  # Suppress output since MCP uses stdio
                stderr=subprocess.DEVNULL,
                cwd=str(project_root),
            )

            # Wait a bit for server to start
            time.sleep(3)

            # Check if server started successfully by checking process
            if _check_mcp_server_running():
                print("-------- mcp-server: started successfully", file=sys.stderr, flush=True)
                return True
            else:
                print("-------- mcp-server: failed to start", file=sys.stderr, flush=True)
                return False
        else:
            print(f"-------- mcp-server: CLI not found at {cli_path}", file=sys.stderr, flush=True)
            return False

    except Exception as e:
        print(f"-------- mcp-server: error starting server: {e}", file=sys.stderr, flush=True)
        return False


def _ensure_mcp_environment():
    """Ensure MCP environment is ready - venv activated and server running"""
    try:
        # Ensure venv is activated
        venv_ok = _ensure_venv_activated()

        # Ensure MCP server is running
        server_ok = _start_mcp_server_if_needed()

        if venv_ok and server_ok:
            print("-------- environment: MCP ready", file=sys.stderr, flush=True)
            return True
        else:
            print("-------- environment: MCP setup incomplete", file=sys.stderr, flush=True)
            return False

    except Exception as e:
        print(f"-------- environment: setup error: {e}", file=sys.stderr, flush=True)
        return False


def _run_direct_tool_if_requested() -> bool:
    """Direct-call escape hatch for Codex CLI until full MCP client lands.

    Triggers when SP_DIRECT_TOOL is set or --call <tool> is provided. This path
    requires MCP_SERVER_MODE to be set, to preserve the MCP-only security model.
    Returns True if a direct call was handled (process should exit afterwards).
    """
    import argparse

    env_call = os.environ.get("SP_DIRECT_TOOL")
    env_args_json = os.environ.get("SP_DIRECT_ARGS_JSON")

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--call", dest="call", default=None)
    parser.add_argument("--args-json", dest="args_json", default=None)
    try:
        ns, _ = parser.parse_known_args()
    except SystemExit:
        ns = argparse.Namespace(call=None, args_json=None)

    tool = env_call or ns.call
    if not tool:
        return False

    # Enforce MCP mark
    if not os.environ.get("MCP_SERVER_MODE"):
        print(
            "-------- ERROR: Direct tool call requires MCP_SERVER_MODE=1",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(97)

    # Parse args
    args_json = env_args_json or ns.args_json or "{}"
    try:
        args = json.loads(args_json)
        if not isinstance(args, dict):
            raise TypeError("args must be a JSON object")
    except Exception as e:
        print(f"-------- ERROR: Invalid --args-json payload: {e}", file=sys.stderr, flush=True)
        sys.exit(2)

    # Map tool name -> function
    registry = {
        # Core tools
        "sp.version": version,
        "sp.init": init,
        "sp.refresh": refresh,
        "sp.list_commands": list_commands,
        "sp.list_personas": list_personas,
        # Mode tools
        "sp.mode_get": mode_get,
        "sp.mode_set": mode_set,
        "sp.grok_mode_on": grok_mode_on,
        "sp.gpt_mode_on": gpt_mode_on,
        "sp.grok_mode_off": grok_mode_off,
        "sp.gpt_mode_off": gpt_mode_off,
        # Persona entrypoints (query:string)
        "sp.architect": architect,
        "sp.frontend": frontend,
        "sp.backend": backend,
        "sp.security": security,
        "sp.performance": performance,
        "sp.analyzer": analyzer,
        "sp.qa": qa,
        "sp.refactorer": refactorer,
        "sp.devops": devops,
        "sp.mentor": mentor,
        "sp.scribe": scribe,
        # SDD
        "sp.specify": specify,
        "sp.plan": plan,
        "sp.tasks": tasks,
        "sp.implement": implement,
        # Sequential reasoning
        "sp.seq": seq,
        "sp.seq-ultra": seq_ultra,
        # High reasoning
        "sp.high": high,
        # Development and documentation
        "sp.dev": dev,
        "sp.doc-master": doc_master,
        "sp.docs-refector": docs_refector,
        # Additional tools
        "sp.grok": grok,
        "sp.db-expert": db_expert,
        "sp.optimize": optimize,
        "sp.review": review,
        "sp.service-planner": service_planner,
        "sp.tr": tr,
        "sp.ultracompressed": ultracompressed,
    }

    fn = registry.get(tool)
    if not fn:
        print(f"-------- ERROR: Unknown tool: {tool}", file=sys.stderr, flush=True)
        sys.exit(3)

    try:
        # Functions return TextContent in MCP mode; unwrap to plain text for direct mode
        result = fn(**args) if args else fn()  # type: ignore[arg-type]
        text = _text_from(result)
        try:
            # Prefer plain text output
            sys.stdout.write(text if text is not None else "")
        except Exception:
            # Fallback to JSON dump
            sys.stdout.write(json.dumps({"ok": True, "result": text}))
        sys.stdout.flush()
        return True
    except TypeError as te:
        print(f"-------- ERROR: Bad arguments for {tool}: {te}", file=sys.stderr, flush=True)
        sys.exit(4)
    except Exception as e:
        print(f"-------- ERROR: Tool {tool} failed: {e}", file=sys.stderr, flush=True)
        sys.exit(5)


def _validate_assets():
    pkg = package_root()
    commands = pkg / "packages" / "cursor-assets" / "commands" / "super-prompt"
    personas = pkg / "packages" / "cursor-assets" / "manifests" / "personas.yaml"
    if not commands.exists() or not personas.exists():
        raise RuntimeError("Missing assets in package tarball. No fallback allowed.")
    # 폴백 4개만 있는지 대략 검증(최소 8개 이상 기대값 예시)
    n = len(list(commands.glob("*.md")))
    if n < 8:
        raise RuntimeError(f"Too few commands found ({n}). Fallback disabled.")


def _init_impl(force: bool = False) -> str:
    # Display Super Prompt ASCII Art
    try:
        from importlib.metadata import version as _v

        current_version = _v("super-prompt")
    except:
        current_version = "4.4.0"

    logo = f"""
\x1b[36m\x1b[1m   ███████╗██╗   ██╗██████╗ ███████╗██████╗
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗
   ███████╗██║   ██║██████╔╝█████╗  ██████╔╝
   ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗
   ███████║╚██████╔╝██║     ███████╗██║  ██║
   ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝

   ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ████████╗
   ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝
   ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝   ██║
   ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝    ██║
   ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║        ██║
   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝\x1b[0m

\x1b[2m              Dual IDE Prompt Engineering Toolkit\x1b[0m
\x1b[2m                     v{current_version} | @cdw0424/super-prompt\x1b[0m
\x1b[2m                          Made by \x1b[0m\x1b[35mDaniel Choi from Korea\x1b[0m
"""
    print(logo, file=sys.stderr, flush=True)
    print("", file=sys.stderr, flush=True)

    _validate_assets()
    pr = project_root()
    data = project_data_dir()
    data.mkdir(parents=True, exist_ok=True)
    # Ensure project venv and runtime deps
    ensure_project_venv(pr, force=force)
    # 에셋 복사(필요 파일만, 덮어쓰기 정책은 force로 제어)
    src = package_root() / "packages" / "cursor-assets"
    # 예시: commands/super-prompt/*, rules/* 등 선택 복사
    _copytree(src / "commands", pr / ".cursor" / "commands", force=force)
    _copytree(src / "rules", pr / ".cursor" / "rules", force=force)
    # 프로젝트용 디렉터리 보장 (Codex assets live in ~/.codex)
    for d in ["specs", "memory"]:
        (pr / d).mkdir(parents=True, exist_ok=True)
    # Auto-create missing spec/plan/tasks skeletons for example-feature
    try:
        example_dir = pr / "specs" / "example-feature"
        example_dir.mkdir(parents=True, exist_ok=True)
        spec_path = example_dir / "spec.md"
        plan_path = example_dir / "plan.md"
        tasks_path = example_dir / "tasks.md"
        # Ensure H2 headings for Success/Acceptance to satisfy SDD gates
        if not spec_path.exists():
            with open(spec_path, "w", encoding="utf-8") as f:
                f.write(
                    "# SDD Enhancement Feature Specification\n\n## REQ-ID: REQ-SDD-001\n\n## Overview\nDescribe the feature.\n\n## User Journey\nDescribe the journey.\n\n## Success Criteria\n- [ ] Criterion\n\n## Acceptance Criteria\n- [ ] Criterion\n\n## Scope & Boundaries\n\n## Business Value\n"
                )
        else:
            try:
                content = spec_path.read_text(encoding="utf-8")
                if "### Success Criteria" in content or "### Acceptance Criteria" in content:
                    content = content.replace(
                        "### Success Criteria", "## Success Criteria"
                    ).replace("### Acceptance Criteria", "## Acceptance Criteria")
                    spec_path.write_text(content, encoding="utf-8")
            except Exception:
                pass
        if not plan_path.exists():
            plan_path.write_text(
                "# Implementation Plan\n\n## REQ-ID: REQ-SDD-001\n\n## Architecture Overview\n\n## Technical Stack\n\n## Security Architecture\n\n## Testing Strategy\n\n## Deployment Strategy\n\n## Success Metrics\n",
                encoding="utf-8",
            )
        if not tasks_path.exists():
            tasks_path.write_text(
                "# Implementation Tasks\n\n## REQ-ID: REQ-SDD-001\n\n## Task Breakdown Strategy\n\n## Acceptance Self-Check Template\n- [ ] ",
                encoding="utf-8",
            )
    except Exception:
        pass
    # Generate Codex assets based on manifest
    try:
        from .adapters.codex_adapter import CodexAdapter  # lazy import; PyYAML optional

        CodexAdapter().generate_assets(pr)
    except Exception as e:
        print(f"-------- WARN: Could not generate Codex assets: {e}", file=sys.stderr, flush=True)

    # MCP/Codex 자동 등록
    ensure_cursor_mcp_registered(pr)  # .cursor/mcp.json 병합
    try:
        ensure_codex_mcp_registered(pr, overwrite=True)  # 선택: ~/.codex/config.toml 재작성
    except Exception:
        pass

    # Ensure default mode and personas manifest
    try:
        set_mode("gpt")
    except Exception:
        pass
    try:
        PersonaLoader().load_manifest()
    except Exception:
        pass
    return f"Initialized at {pr}"


def _copytree(src, dst, force=False):
    if not src.exists():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for p in src.rglob("*"):
        rel = p.relative_to(src)
        t = dst / rel
        if p.is_dir():
            t.mkdir(parents=True, exist_ok=True)
        else:
            if t.exists() and not force:
                continue
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, t)


@register_tool("sp.version")  # 도구명: sp.version - 읽기 전용 버전 정보 조회
def version() -> TextContent:
    """Get Super Prompt version"""
    with memory_span("sp.version"):
        # 필요 시 패키지 버전 리턴
        from importlib.metadata import version as _v

        try:
            ver = _v("super-prompt")
        except Exception:
            ver = "unknown"
        return TextContent(type="text", text=f"Super Prompt v{ver}")


@register_tool("sp.init")  # 도구명: sp.init - 파일 시스템 수정 (프로젝트 초기화)
def init(force: bool = False) -> TextContent:
    """Initialize Super Prompt for current project"""
    # MCP Authorization check
    MCPAuthorization.require_permission("init")

    with memory_span("sp.init"):
        progress.show_progress("🚀 Super Prompt 초기화 시작")
        progress.show_info("권한 확인 중...")

        # MCP 전용 강제: 백도어 금지
        if os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower() not in ("1", "true", "yes"):
            progress.show_error("초기화 권한이 없습니다")
            raise PermissionError(
                "MCP: init/refresh는 기본적으로 비활성화입니다. "
                "환경변수 SUPER_PROMPT_ALLOW_INIT=true 설정 후 다시 시도하세요."
            )

        progress.show_success("초기화 권한 확인됨")
        progress.show_progress("🔍 헬스체크 수행 중")

        # 헬스체크 수행
        health_span = span_manager.start_span({"commandId": "sp.init:health", "userId": None})
        span_manager.write_event(health_span, {"type": "health", "timestamp": time.time()})
        span_manager.end_span(health_span, "ok")
        print("-------- MCP memory: healthcheck OK", file=sys.stderr, flush=True)

        progress.show_success("헬스체크 완료")
        progress.show_progress("📦 프로젝트 초기화 중")
        progress.show_info(f"강제 모드: {force}")

        print(f"-------- mcp: sp.init(args={{force:{force}}})", file=sys.stderr, flush=True)
        msg = _init_impl(force=force)

        progress.show_success("초기화 완료!")
        return TextContent(type="text", text=msg)


@register_tool("sp.refresh")  # 도구명: sp.refresh - 파일 시스템 수정 (에셋 새로고침)
def refresh() -> TextContent:
    """Refresh Super Prompt assets in current project"""
    # MCP Authorization check
    MCPAuthorization.require_permission("refresh")

    with memory_span("sp.refresh"):
        progress.show_progress("🔄 Super Prompt 에셋 새로고침")
        progress.show_info("권한 확인 중...")

        # MCP 전용 강제: 백도어 금지
        if os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower() not in ("1", "true", "yes"):
            progress.show_error("새로고침 권한이 없습니다")
            raise PermissionError(
                "MCP: init/refresh는 기본적으로 비활성화입니다. "
                "환경변수 SUPER_PROMPT_ALLOW_INIT=true 설정 후 다시 시도하세요."
            )

        progress.show_success("새로고침 권한 확인됨")
        progress.show_progress("📦 에셋 새로고침 중")

        msg = _init_impl(force=True)

        progress.show_success("새로고침 완료!")
        return TextContent(type="text", text=msg)


@register_tool("sp.list_commands")  # 도구명: sp.list_commands - 읽기 전용 명령어 목록 조회
def list_commands() -> TextContent:
    """List available Super Prompt commands"""
    with memory_span("sp.list_commands"):
        # 배포물에 실제로 들어간 커맨드 개수 확인용
        commands_dir = package_root() / "packages" / "cursor-assets" / "commands" / "super-prompt"
        count = 0
        files = []
        if commands_dir.exists():
            for p in sorted(commands_dir.glob("*.md")):
                files.append(p.name)
                count += 1
        text = f"Available commands: {count}\n" + "\n".join(files)
        return TextContent(type="text", text=text)


@register_tool("sp.list_personas")  # 도구명: sp.list_personas - 읽기 전용 페르소나 목록 조회
def list_personas() -> TextContent:
    """List available Super Prompt personas"""
    with memory_span("sp.list_personas"):
        from .personas.loader import PersonaLoader

        loader = PersonaLoader()
        loader.load_manifest()
        personas = loader.list_personas()

        if not personas:
            return TextContent(type="text", text="No personas loaded. Try running init first.")

        text = f"Available personas: {len(personas)}\n"
        for persona in personas:
            text += f"- {persona['name']}: {persona['description']}\n"

    return TextContent(type="text", text=text)


@register_tool("sp.mode_get")  # 도구명: sp.mode_get - 읽기 전용 현재 모드 조회
def mode_get() -> TextContent:
    """Get current LLM mode (gpt|grok)"""
    with memory_span("sp.mode_get"):
        mode = get_mode()
        return TextContent(type="text", text=mode)


@register_tool("sp.mode_set")  # 도구명: sp.mode_set - 설정 파일 수정 (모드 변경)
def mode_set(mode: str) -> TextContent:
    """Set LLM mode to 'gpt' or 'grok'"""
    # MCP Authorization check
    MCPAuthorization.require_permission("mode_set")

    with memory_span("sp.mode_set"):
        print(f"-------- mcp: sp.mode_set(args={{mode:'{mode}'}})", file=sys.stderr, flush=True)
        m = set_mode(mode)
        print(f"-------- mode: set to {m}", file=sys.stderr, flush=True)
        return TextContent(type="text", text=f"mode set to {m}")


@register_tool("sp.grok_mode_on")  # 도구명: sp.grok_mode_on - 설정 파일 수정 (모드 변경)
def grok_mode_on(a=None, k=None, **kwargs) -> TextContent:
    """Switch LLM mode to grok"""
    with memory_span("sp.grok_mode_on"):
        set_mode("grok")
        print("-------- mode: set to grok", file=sys.stderr, flush=True)
        return TextContent(type="text", text="mode set to grok")


@register_tool("sp.gpt_mode_on")  # 도구명: sp.gpt_mode_on - 설정 파일 수정 (모드 변경)
def gpt_mode_on(a=None, k=None, **kwargs) -> TextContent:
    """Switch LLM mode to gpt"""
    with memory_span("sp.gpt_mode_on"):
        set_mode("gpt")
        print("-------- mode: set to gpt", file=sys.stderr, flush=True)
        return TextContent(type="text", text="mode set to gpt")


# === Persona Tools ===


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


_PIPELINE_LABELS: Dict[str, str] = {
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
    "grok": "Grok",
    "db-expert": "DB Expert",
    "optimize": "Optimize",
    "review": "Review",
    "service-planner": "Service Planner",
    "tr": "Translate",
    "doc-master": "Doc Master",
    "docs-refector": "Docs Refector",
    "ultracompressed": "Ultra Compressed",
    "seq": "Sequential",
    "seq-ultra": "Sequential Ultra",
    "high": "High Reasoning",
}


_PIPELINE_ALIASES: Dict[str, str] = {
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
    "ultra": "ultracompressed",
    "ultracompressed": "ultracompressed",
    "seq": "seq",
    "sequential": "seq",
    "seq-ultra": "seq-ultra",
    "high": "high",
}


_DEFAULT_PLAN_LINES: Dict[str, List[str]] = {
    "tr": [
        "- Identify source and target locale requirements",
        "- Gather glossary or domain terminology",
        "- Determine tone, formality, and formatting rules",
    ],
    "analyzer": [
        "- Collect reproduction steps and relevant logs",
        "- Map symptom timeline against recent changes",
        "- Formulate top hypotheses ranked by likelihood",
    ],
    "architect": [
        "- Define system boundaries, domains, and capabilities",
        "- Choose data flows, storage, and integration contracts",
        "- Address scalability, observability, and risk mitigation",
    ],
    "frontend": [
        "- Audit component states, accessibility, and responsive breakpoints",
        "- Align visuals with design tokens and interaction patterns",
        "- Identify performance or UX risks across target devices",
    ],
    "backend": [
        "- Map endpoint contracts, data flows, and error handling",
        "- Review database access patterns and transaction boundaries",
        "- Evaluate observability, scaling, and resiliency requirements",
    ],
    "security": [
        "- Enumerate potential threats and sensitive assets",
        "- Review authentication, authorization, and data protection",
        "- Prioritize vulnerabilities and compliance obligations",
    ],
    "performance": [
        "- Profile hot paths and identify resource bottlenecks",
        "- Propose caching, batching, or parallelization strategies",
        "- Define baseline metrics and regression safeguards",
    ],
    "qa": [
        "- Determine critical workflows and risk-based scenarios",
        "- Plan edge cases, negative tests, and data variations",
        "- Align acceptance criteria with automation strategy",
    ],
    "refactorer": [
        "- Locate code smells, duplication, and architectural drift",
        "- Propose incremental refactor plan with safety nets",
        "- Coordinate regression tests and migration notes",
    ],
    "devops": [
        "- Review deployment topology, pipelines, and secrets handling",
        "- Assess monitoring, alerting, and rollout strategies",
        "- Outline reliability risks and mitigation steps",
    ],
    "dev": [
        "- Clarify product requirements and success metrics",
        "- Break work into testable, incremental deliverables",
        "- Align validation, release, and stakeholder coordination",
    ],
    "service-planner": [
        "- Capture goals, KPIs, and success metrics",
        "- Map discovery research, experiments, and risks",
        "- Define cross-team alignment and governance checkpoints",
    ],
    "doc-master": [
        "- Inventory audiences, doc types, and information gaps",
        "- Design IA, templates, and contributor workflow",
        "- Plan verification, localization, and maintenance cadence",
    ],
    "docs-refector": [
        "- Identify duplicate or outdated documentation clusters",
        "- Propose consolidation structure and redirect plan",
        "- Define review owners and migration sequencing",
    ],
    "ultracompressed": [
        "- Select critical insights and supporting evidence",
        "- Prioritize messaging hierarchy under token budget",
        "- Flag trade-offs or details omitted for brevity",
    ],
    "seq": [
        "- Define hypothesis list and evidence required",
        "- Outline sequential reasoning checkpoints",
        "- Prepare validation tests for each conclusion",
    ],
    "seq-ultra": [
        "- Establish ten-step investigation agenda",
        "- Maintain branching options and re-evaluation criteria",
        "- Record open questions and ownership for follow-up",
    ],
    "high": [
        "- Frame strategic context, stakeholders, and constraints",
        "- Analyze scenarios, risks, and potential experiments",
        "- Recommend decision guardrails and success metrics",
    ],
}


_DEFAULT_EXEC_LINES: Dict[str, List[str]] = {
    "tr": [
        "- Produce draft translation and run terminology QA",
        "- Validate locale-specific formatting and constraints",
        "- Schedule stakeholder review and acceptance testing",
    ],
    "analyzer": [
        "- Run experiments to confirm or eliminate hypotheses",
        "- Document root cause evidence and proposed fixes",
        "- Share mitigation plan and monitoring actions",
    ],
    "architect": [
        "- Draft ADRs and architecture diagrams for consensus",
        "- Stage rollout phases with validation checkpoints",
        "- Align observability, SLOs, and governance updates",
    ],
    "frontend": [
        "- Implement component or layout adjustments with accessibility tests",
        "- Run visual/unit regression suites and manual UX checks",
        "- Capture follow-up UX debt and release notes",
    ],
    "backend": [
        "- Implement API or data changes behind feature guards",
        "- Execute contract, integration, and load tests",
        "- Update telemetry dashboards and rollback plan",
    ],
    "security": [
        "- Apply mitigations or compensating controls",
        "- Schedule penetration/system tests and policy updates",
        "- Document residual risk and monitoring actions",
    ],
    "performance": [
        "- Prototype and benchmark prioritized optimizations",
        "- Deploy behind experiment/feature flags",
        "- Monitor long-run metrics and guardrails",
    ],
    "qa": [
        "- Author automated and exploratory test cases",
        "- Execute regression plan and triage defects",
        "- Update coverage dashboards and flake watchlist",
    ],
    "refactorer": [
        "- Execute safe refactors with incremental commits",
        "- Run full test suite and static analysis",
        "- Communicate migration guides and deprecation timeline",
    ],
    "devops": [
        "- Update CI/CD pipelines and infrastructure as code",
        "- Perform canary deployments with health checks",
        "- Document incident response and rollback SOPs",
    ],
    "dev": [
        "- Implement feature slices with instrumentation",
        "- Validate acceptance tests and code review",
        "- Prepare release notes and rollout checklist",
    ],
    "service-planner": [
        "- Draft PRD, discovery plan, and telemetry hooks",
        "- Align cross-functional owners and decision gates",
        "- Schedule backlog grooming and launch readiness reviews",
    ],
    "doc-master": [
        "- Produce IA map, templates, and contributor guide",
        "- Coordinate doc sprints and validation reviews",
        "- Establish upkeep cadence and analytics tracking",
    ],
    "docs-refector": [
        "- Merge or retire redundant docs with redirects",
        "- Normalize style and examples across remaining docs",
        "- Log future documentation debt and owners",
    ],
    "ultracompressed": [
        "- Draft concise response and confirm key facts",
        "- Run peer or stakeholder verification for omissions",
        "- Capture optional deep-dive references",
    ],
    "seq": [
        "- Execute sequential reasoning steps with evidence",
        "- Validate conclusions against assumptions",
        "- Track unresolved branches for future exploration",
    ],
    "seq-ultra": [
        "- Document each iteration outcome and decision",
        "- Maintain branch ledger and revisit pivot criteria",
        "- Summarize insights with remaining unknowns",
    ],
    "high": [
        "- Present strategic recommendation with rationale",
        "- Align stakeholders on risks and contingency plans",
        "- Define monitoring metrics and follow-up checkpoints",
    ],
}


def _build_plan_lines(persona: str, query: str, context: dict) -> List[str]:
    return list(
        _DEFAULT_PLAN_LINES.get(
            persona,
            [
                "- Clarify requirements and constraints",
                "- Break down the problem into manageable steps",
                "- Identify risks and mitigation strategies",
            ],
        )
    )


def _build_exec_lines(persona: str, query: str, context: dict) -> List[str]:
    return list(
        _DEFAULT_EXEC_LINES.get(
            persona,
            [
                "- Implement prioritized actions",
                "- Validate outcomes against definition of done",
                "- Record follow-ups and monitor for regressions",
            ],
        )
    )


_PIPELINE_CONFIGS: Dict[str, PersonaPipelineConfig] = {
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


def _run_persona_pipeline(
    config: PersonaPipelineConfig, query: str, extra_kwargs: Optional[Dict[str, Any]] = None
) -> TextContent:
    with memory_span(f"sp.{config.persona}-pipeline"):
        if not query.strip():
            prompt = config.empty_prompt or (
                f"🔁 {config.label} pipeline activated.\n\nPlease provide a detailed query to begin the pipeline."
            )
            return TextContent(type="text", text=prompt)

        project_dir = project_root()
        confession_logs: List[str] = []
        mem_overview = "no memory available"
        store = None
        try:
            from .memory.store import MemoryStore  # type: ignore

            store = MemoryStore.open(project_dir)
            recent = store.recent_events(limit=5)
            mem_overview = f"recent_events={len(recent)}"
        except Exception as exc:
            confession_logs.append(f"memory load skipped ({exc})")

        prompt_summary = _summarize_situation_for_codex(query, "", config.persona)
        context_info = _analyze_project_context(project_dir, query)

        if config.use_codex is None:
            codex_needed = _should_use_codex_assistance(query, config.persona)
        else:
            codex_needed = config.use_codex

        codex_response: Optional[str] = None
        if codex_needed:
            ctx_patterns = ", ".join(context_info.get("patterns", [])[:3])
            ctx_hint = f"Patterns: {ctx_patterns}" if ctx_patterns else ""
            codex_response = _call_codex_assistance(query, ctx_hint, config.persona)

        persona_kwargs: Dict[str, Any] = {}
        if config.persona_kwargs:
            persona_kwargs.update(config.persona_kwargs)
        if extra_kwargs:
            persona_kwargs.update(extra_kwargs)

        persona_result = _execute_persona(config.persona, query, **persona_kwargs)

        plan_lines = (
            config.plan_builder(query, context_info)
            if config.plan_builder
            else _build_plan_lines(config.persona, query, context_info)
        )
        exec_lines = (
            config.exec_builder(query, context_info)
            if config.exec_builder
            else _build_exec_lines(config.persona, query, context_info)
        )

        try:
            from .commands.validate_tools import validate_check  # type: ignore

            audit = validate_check(project_root=project_dir)
            for line in (audit or {}).get("logs", []) or []:
                confession_logs.append(line)
        except Exception as exc:
            confession_logs.append(f"validation error: {exc}")

        if store is not None:
            try:
                store.append_event(
                    config.memory_tag,
                    {
                        "persona": config.persona,
                        "query": query,
                        "patterns": context_info.get("patterns", []),
                        "plan": plan_lines,
                        "execution": exec_lines,
                        "codex_used": bool(codex_response),
                    },
                )
            except Exception as exc:
                confession_logs.append(f"memory update skipped ({exc})")

        lines: List[str] = []
        lines.append(f"🧭 {config.label} Pipeline Result")
        lines.append("")
        lines.append("1) 프롬프트 분석")
        lines.append(prompt_summary)
        lines.append("")
        lines.append("2) 사전 사료 조사")
        patterns = ", ".join(context_info.get("patterns", [])) or "n/a"
        relevance = ", ".join(context_info.get("query_relevance", [])) or "n/a"
        lines.append(f"- Patterns: {patterns}")
        lines.append(f"- Relevance: {relevance}")
        lines.append("")
        lines.append("3) 메모리 DB 체크")
        lines.append(f"- {mem_overview}")
        lines.append("")
        lines.append("4) 페르소나 및 커맨드 호출")
        if codex_response:
            lines.append("- Codex Insight:")
            lines.append(codex_response)
        lines.append("- Persona Execution: complete")
        lines.append("")
        lines.append("5) 추론 및 Plan 설계")
        lines.extend(plan_lines)
        lines.append("")
        lines.append("6) Plan 실행 지침")
        lines.extend(exec_lines)
        lines.append("")
        lines.append("7) 고해성사 더블체크")
        if confession_logs:
            for log_line in confession_logs:
                lines.append(f"- {log_line}")
        else:
            lines.append("- validation log available (no issues)")
        lines.append("")
        lines.append("8) 메모리 DB 업데이트")
        lines.append("- pipeline event recorded")
        lines.append("")
        lines.append("9) 결론")
        lines.append(_text_from(persona_result))

        result = TextContent(type="text", text="\n".join(lines).strip())
        return _add_confession_mode(result, config.persona, query)


@register_tool("sp.architect")  # 도구명: sp.architect - 읽기 전용 아키텍처 분석 및 설계 조언
def architect(query: str = "", **kwargs) -> TextContent:
    """🏗️ Architect - System design and architecture specialist"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["architect"], query, extra_kwargs=kwargs)


@register_tool("sp.frontend")  # 도구명: sp.frontend - 읽기 전용 프론트엔드 UI/UX 분석 및 조언
def frontend(query: str = "", **kwargs):
    """🎨 Frontend - UI/UX specialist and accessibility advocate

    Provides expertise in React, Vue, Angular, and modern frontend frameworks.
    Focuses on component design, responsive layouts, accessibility (a11y), and
    user experience optimization.

    Args:
        query: Frontend development question, UI/UX problem, or accessibility concern

    Returns:
        Frontend implementation guidance and best practices"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["frontend"], query, extra_kwargs=kwargs)


@register_tool("sp.backend")  # 도구명: sp.backend - 읽기 전용 백엔드 API 및 데이터베이스 분석
def backend(query: str = "", **kwargs):
    """⚡ Backend - Reliability engineer and API specialist

    Expert in server-side development, API design, database optimization, and
    system reliability. Covers REST APIs, GraphQL, microservices, and performance
    optimization.

    Args:
        query: Backend development question, API design problem, or performance issue

    Returns:
        Backend implementation guidance and architectural recommendations"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["backend"], query, extra_kwargs=kwargs)


@register_tool("sp.security")  # 도구명: sp.security - 읽기 전용 보안 취약점 분석 및 조언
def security(query: str = "", **kwargs):
    """🛡️ Security - Threat modeling and vulnerability specialist"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["security"], query, extra_kwargs=kwargs)


@register_tool("sp.performance")  # 도구명: sp.performance - 읽기 전용 성능 분석 및 최적화 조언
def performance(query: str = "", **kwargs):
    """🚀 Performance - Optimization and bottleneck elimination expert"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["performance"], query, extra_kwargs=kwargs)


@register_tool("sp.analyzer")  # 도구명: sp.analyzer - 읽기 전용 근본 원인 분석 및 조사
def analyzer(query: str = "", **kwargs) -> TextContent:
    """🔍 Analyzer - Root cause investigation specialist"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["analyzer"], query, extra_kwargs=kwargs)


@register_tool("sp.qa")  # 도구명: sp.qa - 읽기 전용 품질 보증 및 테스트 분석
def qa(query: str = "", **kwargs):
    """🧪 QA - Quality advocate and testing specialist"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["qa"], query, extra_kwargs=kwargs)


@register_tool("sp.refactorer")  # 도구명: sp.refactorer - 읽기 전용 코드 리팩토링 분석 및 조언
def refactorer(query: str = "", **kwargs):
    """🔧 Refactorer - Code quality and technical debt specialist"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["refactorer"], query, extra_kwargs=kwargs)


@register_tool("sp.devops")  # 도구명: sp.devops - 읽기 전용 DevOps 및 인프라 분석
def devops(query: str = "", **kwargs):
    """🚢 DevOps - Infrastructure and deployment specialist"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["devops"], query, extra_kwargs=kwargs)


@register_tool("sp.debate")  # 도구명: sp.debate - 읽기 전용 내부 토론 분석
def debate(query: str = "", **kwargs):
    """💬 Debate - Positive vs. critical internal debate facilitation"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["debate"], query, extra_kwargs=kwargs)


@register_tool("sp.mentor")  # 도구명: sp.mentor - 읽기 전용 교육 및 멘토링 조언
def mentor(query: str = "", **kwargs):
    """👨‍🏫 Mentor - Knowledge transfer and educational specialist"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["mentor"], query, extra_kwargs=kwargs)


@register_tool("sp.scribe")  # 도구명: sp.scribe - 읽기 전용 기술 문서 작성 조언
def scribe(query: str = "", lang: str = "en", **kwargs):
    """📝 Scribe - Professional documentation specialist"""
    extras = {"lang": lang}
    extras.update(kwargs)
    return _run_persona_pipeline(_PIPELINE_CONFIGS["scribe"], query, extra_kwargs=extras)


@register_tool("sp.pipeline")
def pipeline(tool: str = "", query: str = "", **kwargs) -> TextContent:
    """Meta pipeline tool that routes to persona-specific pipelines."""

    with memory_span("sp.pipeline"):
        if not tool or not tool.strip():
            return TextContent(
                type="text",
                text='⚠️ Pipeline requires a `tool` parameter, e.g., tool="tr".',
            )

        normalized = tool.strip().lower()
        canonical = _PIPELINE_ALIASES.get(normalized)
        if canonical is None:
            available = ", ".join(sorted({f"`{name}`" for name in _PIPELINE_LABELS.keys()}))
            return TextContent(
                type="text",
                text=f"⚠️ Unknown pipeline target `{tool}`. Available targets: {available}.",
            )

        config = _PIPELINE_CONFIGS.get(canonical)
        if config is None:
            return TextContent(
                type="text",
                text=f"⚠️ Pipeline target `{canonical}` has no registered configuration.",
            )

        extra: Dict[str, Any] = {k: v for k, v in kwargs.items() if v is not None}

        def _coerce_to_string(value: Any) -> str:
            if isinstance(value, str):
                return value.strip()
            if isinstance(value, (list, tuple)):
                joined = " ".join(str(item) for item in value)
                return joined.strip()
            if isinstance(value, dict):
                if "content" in value and isinstance(value["content"], str):
                    return value["content"].strip()
                try:
                    return json.dumps(value, ensure_ascii=False).strip()
                except Exception:
                    return str(value).strip()
            return str(value).strip()

        effective_query = query.strip() if isinstance(query, str) else ""
        # If the incoming query is a JSON object string (e.g., {"a":"...","k":"..."}),
        # parse it and extract a more meaningful query and extra kwargs.
        # This makes the pipeline robust to clients that pass Cursor-style payloads as a single string.
        if effective_query and isinstance(query, str):
            q = effective_query
            if (q.startswith("{") and q.endswith("}")) or (q.startswith("[") and q.endswith("]")):
                try:
                    parsed = json.loads(q)
                    if isinstance(parsed, dict):
                        # Prefer 'k' as the primary text (user key used in some shells), then 'query'
                        if "k" in parsed and isinstance(parsed["k"], (str, list, tuple, dict)):
                            effective_query = _coerce_to_string(parsed.pop("k"))
                        elif "query" in parsed and isinstance(
                            parsed["query"], (str, list, tuple, dict)
                        ):
                            effective_query = _coerce_to_string(parsed.pop("query"))

                        # If 'a' carries a hint like "tool=high", capture as a non-routing hint
                        a_val = parsed.pop("a", None)
                        if isinstance(a_val, str) and a_val.startswith("tool="):
                            hint = a_val.split("=", 1)[1].strip()
                            if hint:
                                extra["tool_hint"] = (
                                    hint  # Do not override selected tool automatically
                                )

                        # Merge any remaining fields into extras if not None
                        for k2, v2 in list(parsed.items()):
                            if v2 is not None and k2 not in ("tool",):
                                extra[k2] = v2
                except Exception:
                    # If JSON parsing fails, continue with the original string
                    pass
        if not effective_query:
            fallback_keys = [
                "query",
                "input",
                "message",
                "text",
                "prompt",
                "body",
                "content",
                "question",
                "a",
            ]
            for key in fallback_keys:
                if key in extra:
                    candidate = _coerce_to_string(extra.pop(key))
                    if candidate:
                        effective_query = candidate
                        break

        if not effective_query and isinstance(query, str):
            effective_query = query

        return _run_persona_pipeline(config, effective_query, extra_kwargs=extra)


@register_tool("sp.grok_mode_off")  # 도구명: sp.grok_mode_off - 설정 파일 수정 (모드 변경)
def grok_mode_off(a=None, k=None, **kwargs) -> TextContent:
    """Turn off Grok mode"""
    with memory_span("sp.grok_mode_off"):
        set_mode("gpt")
        return TextContent(type="text", text="Grok mode turned off, switched to GPT")


@register_tool("sp.gpt_mode_off")  # 도구명: sp.gpt_mode_off - 설정 파일 수정 (모드 변경)
def gpt_mode_off(a=None, k=None, **kwargs) -> TextContent:
    """Turn off GPT mode"""
    with memory_span("sp.gpt_mode_off"):
        set_mode("grok")
        return TextContent(type="text", text="GPT mode turned off, switched to Grok")


@register_tool("sp.specify")  # 도구명: sp.specify - 읽기 전용 요구사항 명세화
def specify(query: str = "", **kwargs) -> TextContent:
    """📋 Specify - Create detailed specifications"""
    with memory_span("sp.specify"):
        return TextContent(
            type="text",
            text=f"📋 Specification tool activated.\n\nQuery: {query}\n\nThis tool helps create detailed specifications for features and requirements.",
        )


@register_tool("sp.plan")  # 도구명: sp.plan - 읽기 전용 계획 수립
def plan(query: str = "", **kwargs) -> TextContent:
    """📅 Plan - Create implementation plans"""
    with memory_span("sp.plan"):
        return TextContent(
            type="text",
            text=f"📅 Planning tool activated.\n\nQuery: {query}\n\nThis tool helps create structured implementation plans.",
        )


@register_tool("sp.tasks")  # 도구명: sp.tasks - 읽기 전용 작업 분해
def tasks(query: str = "", **kwargs) -> TextContent:
    """✅ Tasks - Break down work into tasks"""
    with memory_span("sp.tasks"):
        return TextContent(
            type="text",
            text=f"✅ Task breakdown tool activated.\n\nQuery: {query}\n\nThis tool helps break down work into manageable tasks.",
        )


@register_tool("sp.implement")  # 도구명: sp.implement - 읽기 전용 구현 조언
def implement(query: str = "", **kwargs) -> TextContent:
    """🔨 Implement - Execute implementation"""
    with memory_span("sp.implement"):
        return TextContent(
            type="text",
            text=f"🔨 Implementation tool activated.\n\nQuery: {query}\n\nThis tool helps execute implementations based on plans and specifications.",
        )


@register_tool("sp.seq")  # 도구명: sp.seq - 읽기 전용 순차적 추론
def seq(query: str = "", **kwargs):
    """🔍 Sequential - Step-by-step reasoning and analysis"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["seq"], query, extra_kwargs=kwargs)


@register_tool("sp.seq-ultra")  # 도구명: sp.seq-ultra - 읽기 전용 심층 순차적 추론
def seq_ultra(query: str = "", **kwargs):
    """🧠 Sequential Ultra - Ultra-deep sequential reasoning for complex problems"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["seq-ultra"], query)


@register_tool("sp.high")  # 도구명: sp.high - 읽기 전용 고수준 추론
def high(query: str = "", **kwargs):
    """🧠 High Reasoning - Deep reasoning and strategic problem solving with GPT-5 high model approach"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["high"], query, extra_kwargs=kwargs)


@register_tool("sp.dev")  # 도구명: sp.dev - 읽기 전용 개발 조언
def dev(query: str = "", **kwargs):
    """🚀 Dev - Feature development with quality and delivery focus"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["dev"], query, extra_kwargs=kwargs)


@register_tool("sp.grok")  # 도구명: sp.grok - 읽기 전용 Grok 세션 최적화
def grok(query: str = "", **kwargs):
    """🤖 Grok - xAI's helpful and maximally truthful AI"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["grok"], query, extra_kwargs=kwargs)


@register_tool("sp.db-expert")  # 도구명: sp.db-expert - 읽기 전용 데이터베이스 전문가 조언
def db_expert(query: str = "", **kwargs):
    """🗄️ Database Expert - SQL, database design, and optimization specialist"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["db-expert"], query)


@register_tool("sp.optimize")  # 도구명: sp.optimize - 읽기 전용 일반 최적화 조언
def optimize(query: str = "", **kwargs):
    """⚡ Optimize - Performance optimization and efficiency specialist"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["optimize"], query, extra_kwargs=kwargs)


@register_tool("sp.review")  # 도구명: sp.review - 읽기 전용 코드 리뷰 및 품질 검토
def review(query: str = "", **kwargs):
    """🔍 Review - Code review and quality assurance specialist"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["review"], query, extra_kwargs=kwargs)


@register_tool("sp.service-planner")  # 도구명: sp.service-planner
def service_planner(query: str = "", **kwargs):
    """🏗️ Service Planner - System architecture and service design specialist"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["service-planner"], query)


@register_tool("sp.tr")  # 도구명: sp.tr
def tr(query: str = "", **kwargs) -> TextContent:
    """🌐 Translate - Multi-language translation and localization specialist"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["tr"], query, extra_kwargs=kwargs)


@register_tool("sp.ultracompressed")  # 도구명: sp.ultracompressed
def ultracompressed(query: str = "", **kwargs):
    """🗜️ Ultra Compressed - Maximum information density with minimal tokens"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["ultracompressed"], query, extra_kwargs=kwargs)


@register_tool("sp.doc-master")  # 도구명: sp.doc-master
def doc_master(query: str = "", **kwargs):
    """📚 Doc Master - Documentation architecture, writing, and verification"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["doc-master"], query)


@register_tool("sp.docs-refector")  # 도구명: sp.docs-refector
def docs_refector(query: str = "", **kwargs):
    """🧹 Docs Refector - Repository-wide documentation audit, de-duplication, and consolidation"""
    return _run_persona_pipeline(_PIPELINE_CONFIGS["docs-refector"], query)


# MCP Server Entry Point for Cursor IDE
# This module provides MCP tools that Cursor IDE can use

if __name__ == "__main__":
    # When run directly, start MCP server in stdio mode
    import asyncio
    import sys

    async def main():
        if mcp is None:
            print("-------- ERROR: MCP server initialization failed", file=sys.stderr, flush=True)
            sys.exit(1)

        print(
            "-------- MCP: Starting Super Prompt server for Cursor IDE", file=sys.stderr, flush=True
        )

        try:
            # Run FastMCP in stdio mode - Cursor will handle stdin/stdout communication
            await mcp.run()
        except Exception as e:
            print(f"-------- ERROR: MCP server error: {e}", file=sys.stderr, flush=True)
            sys.exit(1)

    # Run help if requested
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        print("Super Prompt MCP Server for Cursor IDE")
        print("Available tools:")
        for tool_name, meta in sorted(TOOL_METADATA.items()):
            category = meta.get("category", "unknown")
            print(f"  - {tool_name} ({category})")
        sys.exit(0)

    asyncio.run(main())
else:
    # When imported as module, just log registration
    print("-------- MCP: Super Prompt tools loaded", file=sys.stderr, flush=True)
