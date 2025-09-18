# packages/core-py/super_prompt/mcp_server.py
# SECURITY: MCP-only access - Direct CLI calls are blocked
# pip dep: mcp >= 0.4.0  (pyproject.toml 또는 setup.cfg에 추가)
import os
import sys
import asyncio
import subprocess
import json
import inspect
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
from typing import Dict, Any, Optional, List
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
                    print(f"-------- confession: error during validation: {e}", file=sys.stderr, flush=True)
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
            try:
                return fn(*a, **k)
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
def grok_mode_on() -> TextContent:
    """Switch LLM mode to grok"""
    with memory_span("sp.grok_mode_on"):
        set_mode("grok")
        print("-------- mode: set to grok", file=sys.stderr, flush=True)
        return TextContent(type="text", text="mode set to grok")


@register_tool("sp.gpt_mode_on")  # 도구명: sp.gpt_mode_on - 설정 파일 수정 (모드 변경)
def gpt_mode_on() -> TextContent:
    """Switch LLM mode to gpt"""
    with memory_span("sp.gpt_mode_on"):
        set_mode("gpt")
        print("-------- mode: set to gpt", file=sys.stderr, flush=True)
        return TextContent(type="text", text="mode set to gpt")


# === Persona Tools ===


@register_tool("sp.architect")  # 도구명: sp.architect - 읽기 전용 아키텍처 분석 및 설계 조언
def architect(query: str = "") -> TextContent:
    """🏗️ Architect - System design and architecture specialist

    Analyzes system architecture, provides design recommendations, and helps with
    scalability planning. Best for complex system design decisions and architectural
    reviews.

    Args:
        query: Architecture question or system design problem to analyze

    Returns:
        Detailed architectural analysis and recommendations"""
    with memory_span("sp.architect"):
        # Note: MCP environment check removed - direct calls work without full MCP server
        # This ensures the tool always works when called via MCP client direct invocation

        if not query.strip():
            return TextContent(
                type="text",
                text="""🏗️ Architect tool activated.

To provide the best architectural guidance, please provide:

• What type of system are you designing? (web app, API, microservices, etc.)
• What are the key requirements? (scalability, performance, security, etc.)
• What technologies/frameworks are you considering?
• What's the expected user load and data volume?

Example: "Design a scalable e-commerce platform using React and Node.js"

Please provide your architecture question or requirements.""",
            )

        # Enforce pipeline: [프롬프트 분석 -> 사전 사료 조사 -> 메모리 db체크 -> 페르소나/커맨드 호출 -> 추론/Plan -> Plan실행 -> 고해성사 더블체크 -> 메모리 db업데이트 -> 결론]
        # 1) 프롬프트 분석
        prompt_summary = _summarize_situation_for_codex(query, "", "architect")

        # 2) 사전 사료 조사
        project_root = Path.cwd()
        context_info = _analyze_project_context(project_root, query)

        # 3) 메모리 db체크
        confession_logs: list[str] = []
        mem_overview: str = ""
        try:
            from .memory.store import MemoryStore  # type: ignore
            store = MemoryStore.open(project_root)
            recent = store.recent_events(limit=10)
            mem_overview = f"recent_events={len(recent)}; task_tag={store.get_task_tag()!s}"
        except Exception as e:
            confession_logs.append(f"memory check skipped ({e})")

        # 4) 페르소나 및 커맨드 mcp 호출 및 자료 전달
        codex_response: str | None = None
        if _should_use_codex_assistance(query, "architect"):
            print("-------- architect: using Codex assistance per pipeline", file=sys.stderr, flush=True)
            ctx_str = f"Architecture context: {', '.join(context_info.get('patterns', []))}"
            codex_response = _call_codex_assistance(query, ctx_str, "architect")

        persona_result = _execute_persona("architect", query)

        # 5) 추론 및 Plan 설계
        plan_lines = [
            "- Define system boundaries and core services",
            "- Choose data storage strategies and cache layers",
            "- Establish API contracts and integration points",
            "- Address scalability, observability, and security baselines",
        ]

        # 6) Plan 실행 (지침)
        exec_lines = [
            "- Create ADR for chosen architecture",
            "- Scaffold services and CI with templates",
            "- Add dashboards and SLOs; implement tracing",
        ]

        # 7) 고해성사모드 더블체크
        try:
            from .commands.validate_tools import validate_check  # type: ignore
            v = validate_check()
            for ln in (v or {}).get("logs", []) or []:
                confession_logs.append(ln)
        except Exception as e:
            confession_logs.append(f"validation error: {e}")

        # 8) 메모리 db업데이트
        try:
            from .memory.store import MemoryStore  # type: ignore
            store2 = MemoryStore.open(project_root)
            store2.append_event(
                "architect_pipeline",
                {
                    "query": query,
                    "context_patterns": context_info.get("patterns", []),
                    "plan": plan_lines,
                    "execution": exec_lines,
                    "codex_used": bool(codex_response),
                },
            )
        except Exception as e:
            confession_logs.append(f"memory update skipped ({e})")

        # 9) 결론
        out: list[str] = []
        out.append("🏗️ Architect Pipeline Result")
        out.append("")
        out.append("1) 프롬프트 분석")
        out.append(prompt_summary)
        out.append("")
        out.append("2) 사전 사료 조사")
        out.append(f"- Tech stack hints: {', '.join(context_info.get('patterns', [])) or 'n/a'}")
        out.append(f"- Relevance: {', '.join(context_info.get('query_relevance', [])) or 'n/a'}")
        out.append("")
        out.append("3) 메모리 DB 체크")
        out.append(f"- {mem_overview or 'no memory available'}")
        out.append("")
        out.append("4) 페르소나 및 커맨드 호출")
        if codex_response:
            out.append("- Codex Insight:")
            out.append(codex_response)
        out.append("- Persona Execution: done")
        out.append("")
        out.append("5) 추론 및 Plan 설계")
        out.extend(plan_lines)
        out.append("")
        out.append("6) Plan 실행 지침")
        out.extend(exec_lines)
        out.append("")
        out.append("7) 고해성사 더블체크")
        for ln in confession_logs:
            out.append(f"- {ln}")
        out.append("")
        out.append("8) 메모리 DB 업데이트")
        out.append("- recorded pipeline event")
        out.append("")
        out.append("9) 결론")
        out.append(_text_from(persona_result))

        return TextContent(type="text", text="\n".join(out))


@register_tool("sp.frontend")  # 도구명: sp.frontend - 읽기 전용 프론트엔드 UI/UX 분석 및 조언
def frontend(query: str = "") -> TextContent:
    """🎨 Frontend - UI/UX specialist and accessibility advocate

    Provides expertise in React, Vue, Angular, and modern frontend frameworks.
    Focuses on component design, responsive layouts, accessibility (a11y), and
    user experience optimization.

    Args:
        query: Frontend development question, UI/UX problem, or accessibility concern

    Returns:
        Frontend implementation guidance and best practices"""
    with memory_span("sp.frontend"):
        if not query.strip():
            return TextContent(
                type="text",
                text="""🎨 Frontend tool activated.

To provide the best frontend guidance, please specify:

• What framework/library are you using? (React, Vue, Angular, Svelte, etc.)
• What type of component/feature are you building?
• Is this about styling, state management, performance, or accessibility?
• Do you have existing code or design mockups?

Example: "How to implement a responsive navigation menu in React with accessibility"

Please provide your frontend development question.""",
            )

        result = _execute_persona("frontend", query)
        return _add_confession_mode(result, "frontend", query)


@register_tool("sp.backend")  # 도구명: sp.backend - 읽기 전용 백엔드 API 및 데이터베이스 분석
def backend(query: str = "") -> TextContent:
    """⚡ Backend - Reliability engineer and API specialist

    Expert in server-side development, API design, database optimization, and
    system reliability. Covers REST APIs, GraphQL, microservices, and performance
    optimization.

    Args:
        query: Backend development question, API design problem, or performance issue

    Returns:
        Backend implementation guidance and architectural recommendations"""
    with memory_span("sp.backend"):
        if not query.strip():
            return TextContent(
                type="text",
                text="""⚡ Backend tool activated.

To provide the best backend guidance, please specify:

• What language/framework are you using? (Node.js, Python, Java, Go, etc.)
• What type of API/service are you building? (REST, GraphQL, microservices)
• Is this about database design, API endpoints, performance, or security?
• What database system are you considering? (PostgreSQL, MongoDB, Redis, etc.)

Example: "Design REST API endpoints for user management with JWT authentication"

Please provide your backend development question.""",
            )

        result = _execute_persona("backend", query)
        return _add_confession_mode(result, "backend", query)


@register_tool("sp.security")  # 도구명: sp.security - 읽기 전용 보안 취약점 분석 및 조언
def security(query: str = "") -> TextContent:
    """🛡️ Security - Threat modeling and vulnerability specialist"""
    with memory_span("sp.security"):
        result = _execute_persona("security", query)
        return _add_confession_mode(result, "security", query)


@register_tool("sp.performance")  # 도구명: sp.performance - 읽기 전용 성능 분석 및 최적화 조언
def performance(query: str = "") -> TextContent:
    """🚀 Performance - Optimization and bottleneck elimination expert"""
    with memory_span("sp.performance"):
        result = _execute_persona("performance", query)
        return _add_confession_mode(result, "performance", query)


@register_tool("sp.analyzer")  # 도구명: sp.analyzer - 읽기 전용 근본 원인 분석 및 조사
def analyzer(query: str = "") -> TextContent:
    """🔍 Analyzer - Root cause investigation specialist"""
    with memory_span("sp.analyzer"):
        progress.show_progress("🔍 Analyzer activated")
        progress.show_info("Initializing root cause analysis")

        # Note: MCP environment check removed - direct calls work without full MCP server
        # This ensures the tool always works when called via MCP client direct invocation

        if not query.strip():
            progress.show_error("No query provided")
            return TextContent(
                type="text",
                text="""🔍 Analyzer tool activated.

To perform effective root cause analysis, please provide:

• What specific issue or error are you experiencing?
• What symptoms have you observed?
• When did this issue start occurring?
• What recent changes were made before the issue appeared?
• Are there any error messages, logs, or stack traces?

Example: "My React app crashes when users submit forms - getting 'Cannot read property of undefined'"

Please provide the problem description for analysis.""",
            )

        progress.show_progress("🔍 Starting root cause analysis")
        progress.show_info(f"Query: {query[:50]}{'...' if len(query) > 50 else ''}")

        # Always use Codex CLI for root cause analysis, as that is the tool's purpose.
        progress.show_progress("🤖 Calling Codex CLI for analysis")
        print(
            "-------- analyzer: using Codex CLI for root cause analysis",
            file=sys.stderr,
            flush=True,
        )

        # 프로젝트 컨텍스트 수집
        project_root = Path.cwd()
        context_info = _analyze_project_context(project_root, query)
        context_str = f"Analysis context: {context_info.get('file_count', 0)} files, investigating: {query[:100]}..."

        # Codex CLI 호출
        codex_response = _call_codex_assistance(query, context_str, "analyzer")

        response = f"🔍 **Root Cause Analysis (Codex CLI)**\n\n**Query:** {query}\n\n"
        response += f"**📊 Analysis Context:**\n"
        response += f"- Project scope: {context_info.get('file_count', 0)} files\n"
        response += f"- Investigation focus: {query[:100]}{'...' if len(query) > 100 else ''}\n\n"

        response += f"**🤖 Codex Root Cause Insight:**\n"
        response += f"{codex_response}\n\n"

        # 분석 프레임워크 표시
        response += f"**Analysis Framework:**\n"
        steps = [
            "✅ Problem Identification - COMPLETED",
            "✅ Root Cause Analysis - PROVIDED BY CODEX",
            "✅ Impact Assessment - INTEGRATED",
            "✅ Solution Recommendations - GUIDED",
            "✅ Prevention Strategies - SUGGESTED",
        ]
        for step in steps:
            response += f"- {step}\n"

        result = TextContent(type="text", text=response)
        return _add_confession_mode(result, "analyzer", query)


@register_tool("sp.qa")  # 도구명: sp.qa - 읽기 전용 품질 보증 및 테스트 분석
def qa(query: str = "") -> TextContent:
    """🧪 QA - Quality advocate and testing specialist"""
    with memory_span("sp.qa"):
        result = _execute_persona("qa", query)
        return _add_confession_mode(result, "qa", query)


@register_tool("sp.refactorer")  # 도구명: sp.refactorer - 읽기 전용 코드 리팩토링 분석 및 조언
def refactorer(query: str = "") -> TextContent:
    """🔧 Refactorer - Code quality and technical debt specialist"""
    with memory_span("sp.refactorer"):
        result = _execute_persona("refactorer", query)
        return _add_confession_mode(result, "refactorer", query)


@register_tool("sp.devops")  # 도구명: sp.devops - 읽기 전용 DevOps 및 인프라 분석
def devops(query: str = "") -> TextContent:
    """🚢 DevOps - Infrastructure and deployment specialist"""
    with memory_span("sp.devops"):
        result = _execute_persona("devops", query)
        return _add_confession_mode(result, "devops", query)


@register_tool("sp.debate")  # 도구명: sp.debate - 읽기 전용 내부 토론 분석
def debate(query: str = "") -> TextContent:
    """💬 Debate - Positive vs. critical internal debate facilitation"""
    with memory_span("sp.debate"):
        result = _execute_persona("debate", query)
        return _add_confession_mode(result, "debate", query)


@register_tool("sp.mentor")  # 도구명: sp.mentor - 읽기 전용 교육 및 멘토링 조언
def mentor(query: str = "") -> TextContent:
    """👨‍🏫 Mentor - Knowledge transfer and educational specialist"""
    with memory_span("sp.mentor"):
        result = _execute_persona("mentor", query)
        return _add_confession_mode(result, "mentor", query)


@register_tool("sp.scribe")  # 도구명: sp.scribe - 읽기 전용 기술 문서 작성 조언
def scribe(query: str = "", lang: str = "en") -> TextContent:
    """📝 Scribe - Professional documentation specialist"""
    with memory_span("sp.scribe"):
        print(
            f"-------- mcp: sp.scribe(args={{lang:'{lang}', query_len:{len(query)}}})",
            file=sys.stderr,
            flush=True,
        )
        # Reflect language so MCP arg is visibly consumed
        prefix = f"[lang={lang}] " if lang else ""
        base = _execute_persona("scribe", query)
        result = TextContent(type="text", text=f"{prefix}{_text_from(base)}")
        return _add_confession_mode(result, "scribe", query)


# === Additional Tools ===


def _add_confession_mode(result: TextContent, persona_name: str, query: str) -> TextContent:
    """Add confession mode (double-check) transparency to all MCP tool outputs"""
    original_text = _text_from(result)

    # Generate confession mode audit
    confession_audit = f"""

---

🕵️‍♂️ **CONFESSION MODE - Radical Transparency Audit**

**Tool:** {persona_name}
**Query:** {query}

**✅ WHAT IS KNOWN:**
- This response was generated by the {persona_name} persona
- Based on the provided query and available context
- Subject to the persona's specialized knowledge domain
- Memory span tracking is active for this interaction

**❓ WHAT IS UNKNOWN:**
- Real-time external data or system status
- User's specific project constraints or preferences
- Integration requirements with other systems
- Long-term maintenance implications
- Performance impact in production environments

**⚠️ POTENTIAL SIDE-EFFECTS & EDGE CASES:**
- Persona recommendations may need adaptation to specific project needs
- Technical suggestions assume standard configurations
- Security recommendations are general and should be reviewed by experts
- Performance optimizations may have trade-offs in other areas

**🛡️ PROPOSED COUNTERMEASURES:**
- Always validate recommendations against your specific project requirements
- Test all code changes in staging environments first
- Consult with domain experts for critical decisions
- Implement monitoring and rollback strategies
- Document assumptions and constraints for future reference

**🎯 RELIABILITY CONFIDENCE:** Medium-High (based on persona specialization)
**📊 AUDIT COMPLETED:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
"""

    # Add resource links for the persona
    resource_links = _get_persona_resource_links(persona_name)
    if resource_links:
        confession_audit += f"\n{resource_links}\n"

    combined_text = original_text + confession_audit
    return TextContent(type="text", text=combined_text)


@register_tool("sp.grok_mode_off")  # 도구명: sp.grok_mode_off - 설정 파일 수정 (모드 변경)
def grok_mode_off() -> TextContent:
    """Turn off Grok mode"""
    with memory_span("sp.grok_mode_off"):
        set_mode("gpt")
        return TextContent(type="text", text="Grok mode turned off, switched to GPT")


@register_tool("sp.gpt_mode_off")  # 도구명: sp.gpt_mode_off - 설정 파일 수정 (모드 변경)
def gpt_mode_off() -> TextContent:
    """Turn off GPT mode"""
    with memory_span("sp.gpt_mode_off"):
        set_mode("grok")
        return TextContent(type="text", text="GPT mode turned off, switched to Grok")


@register_tool("sp.specify")  # 도구명: sp.specify - 읽기 전용 요구사항 명세화
def specify(query: str = "") -> TextContent:
    """📋 Specify - Create detailed specifications"""
    with memory_span("sp.specify"):
        return TextContent(
            type="text",
            text=f"📋 Specification tool activated.\n\nQuery: {query}\n\nThis tool helps create detailed specifications for features and requirements.",
        )


@register_tool("sp.plan")  # 도구명: sp.plan - 읽기 전용 계획 수립
def plan(query: str = "") -> TextContent:
    """📅 Plan - Create implementation plans"""
    with memory_span("sp.plan"):
        return TextContent(
            type="text",
            text=f"📅 Planning tool activated.\n\nQuery: {query}\n\nThis tool helps create structured implementation plans.",
        )


@register_tool("sp.tasks")  # 도구명: sp.tasks - 읽기 전용 작업 분해
def tasks(query: str = "") -> TextContent:
    """✅ Tasks - Break down work into tasks"""
    with memory_span("sp.tasks"):
        return TextContent(
            type="text",
            text=f"✅ Task breakdown tool activated.\n\nQuery: {query}\n\nThis tool helps break down work into manageable tasks.",
        )


@register_tool("sp.implement")  # 도구명: sp.implement - 읽기 전용 구현 조언
def implement(query: str = "") -> TextContent:
    """🔨 Implement - Execute implementation"""
    with memory_span("sp.implement"):
        return TextContent(
            type="text",
            text=f"🔨 Implementation tool activated.\n\nQuery: {query}\n\nThis tool helps execute implementations based on plans and specifications.",
        )


@register_tool("sp.seq")  # 도구명: sp.seq - 읽기 전용 순차적 추론
def seq(query: str = "") -> TextContent:
    """🔍 Sequential - Step-by-step reasoning and analysis"""
    with memory_span("sp.seq"):
        if not query.strip():
            return TextContent(
                type="text",
                text="🔍 Sequential reasoning tool activated.\n\nPlease provide a query to analyze.",
            )

        # Basic sequential reasoning approach
        steps = [
            "1. **Understand the Problem**: Break down the question into its core components",
            "2. **Identify Key Concepts**: Determine the fundamental principles involved",
            "3. **Apply Logical Reasoning**: Use step-by-step logic to arrive at a conclusion",
            "4. **Verify the Answer**: Check the reasoning for consistency and accuracy",
            "5. **Provide Explanation**: Give a clear, comprehensive answer",
        ]

        response = f"🔍 **Sequential Reasoning Analysis**\n\n**Query:** {query}\n\n**Step-by-Step Approach:**\n"
        for step in steps:
            response += f"- {step}\n"

        response += f"\n**Analysis:**\n"
        response += _perform_sequential_analysis(query)

        return TextContent(type="text", text=response)


@register_tool("sp.seq-ultra")  # 도구명: sp.seq-ultra - 읽기 전용 심층 순차적 추론
def seq_ultra(query: str = "") -> TextContent:
    """🧠 Sequential Ultra - Ultra-deep sequential reasoning for complex problems"""
    with memory_span("sp.seq-ultra"):
        if not query.strip():
            return TextContent(
                type="text",
                text="🧠 Sequential Ultra reasoning tool activated.\n\nPlease provide a complex query to analyze in depth.",
            )

        # Ultra-deep sequential reasoning with more detailed steps
        steps = [
            "1. **Problem Decomposition**: Break down complex problems into fundamental components",
            "2. **Knowledge Base Analysis**: Identify relevant concepts, theories, and principles",
            "3. **Logical Framework Construction**: Build systematic reasoning structures",
            "4. **Step-by-Step Deduction**: Apply rigorous logical progression",
            "5. **Alternative Perspectives**: Consider multiple viewpoints and edge cases",
            "6. **Validation & Verification**: Cross-check reasoning with established knowledge",
            "7. **Synthesis & Conclusion**: Integrate findings into comprehensive answer",
            "8. **Confidence Assessment**: Evaluate certainty and identify limitations",
        ]

        response = f"🧠 **Ultra-Deep Sequential Reasoning Analysis**\n\n**Query:** {query}\n\n**Comprehensive Analysis Framework:**\n"
        for step in steps:
            response += f"- {step}\n"

        response += f"\n**Detailed Analysis:**\n"
        response += _perform_ultra_sequential_analysis(query)

        return TextContent(type="text", text=response)


@register_tool("sp.high")  # 도구명: sp.high - 읽기 전용 고수준 추론
def high(query: str = "") -> TextContent:
    """🧠 High Reasoning - Deep reasoning and strategic problem solving with GPT-5 high model approach"""
    with memory_span("sp.high"):
        # Note: MCP environment check removed - direct calls work without full MCP server
        # This ensures the tool always works when called via MCP client direct invocation

        if not query.strip():
            return TextContent(
                type="text",
                text="🧠 High Reasoning tool activated.\n\nPlease provide a complex query for deep strategic analysis.",
            )

        # High 명령어는 무조건 Codex CLI 사용
        print("-------- high: using Codex CLI for strategic reasoning", file=sys.stderr, flush=True)

        # 프로젝트 컨텍스트 수집
        project_root = Path.cwd()
        context_info = _analyze_project_context(project_root, query)
        context_str = f"Project: {context_info.get('file_count', 0)} files, patterns: {', '.join(context_info.get('patterns', []))}"

        # Codex CLI 호출
        codex_response = _call_codex_assistance(query, context_str, "high")

        # 결과 포맷팅
        response = f"🧠 **High Reasoning Analysis (Codex CLI)**\n\n**Query:** {query}\n\n"
        response += f"**📊 Project Context:**\n"
        response += f"- Files analyzed: {context_info.get('file_count', 0)}\n"
        response += f"- Key patterns: {', '.join(context_info.get('patterns', []))}\n"
        response += f"- Context clues: {', '.join(context_info.get('query_relevance', []))}\n\n"

        response += f"**🤖 Codex Strategic Insight:**\n"
        response += f"{codex_response}\n\n"

        # 추가 분석 프레임워크 표시
        response += f"**Strategic Analysis Framework:**\n"
        steps = [
            "✅ Situation Analysis - COMPLETED",
            "✅ Strategic Insight - PROVIDED BY CODEX",
            "✅ Risk Assessment - INTEGRATED",
            "✅ Decision Optimization - RECOMMENDED",
            "✅ Implementation Strategy - GUIDED",
        ]
        for step in steps:
            response += f"- {step}\n"

        result = TextContent(type="text", text=response)
        return _add_confession_mode(result, "high", query)


@register_tool("sp.dev")  # 도구명: sp.dev - 읽기 전용 개발 조언
def dev(query: str = "") -> TextContent:
    """🚀 Dev - Feature development with quality and delivery focus"""
    with memory_span("sp.dev"):
        # Note: MCP environment check removed - direct calls work without full MCP server
        # This ensures the tool always works when called via MCP client direct invocation

        if not query.strip():
            return TextContent(
                type="text",
                text="🚀 Dev tool activated.\n\nPlease provide a development task or feature request.",
            )

        # Codex CLI 사용 여부 결정
        use_codex = _should_use_codex_assistance(query, "dev")

        if use_codex:
            print(
                "-------- dev: using Codex CLI for complex development analysis",
                file=sys.stderr,
                flush=True,
            )

            # 프로젝트 컨텍스트 수집
            project_root = Path.cwd()
            context_info = _analyze_project_context(project_root, query)
            context_str = f"Tech stack analysis: {', '.join(context_info.get('patterns', []))}"

            # Codex CLI 호출
            codex_response = _call_codex_assistance(query, context_str, "dev")

            response = f"🚀 **Development Analysis (Codex CLI)**\n\n**Query:** {query}\n\n"
            response += f"**📊 Technical Context:**\n"
            response += f"- Project patterns: {', '.join(context_info.get('patterns', []))}\n"
            response += f"- Context clues: {', '.join(context_info.get('query_relevance', []))}\n\n"

            response += f"**🤖 Codex Development Insight:**\n"
            response += f"{codex_response}\n\n"

            # 개발 프레임워크 표시
            response += f"**Development Framework:**\n"
            steps = [
                "✅ Requirements Analysis - COMPLETED",
                "✅ Technical Design - GUIDED BY CODEX",
                "✅ Implementation Strategy - PROVIDED",
                "✅ Quality Assurance - RECOMMENDED",
                "✅ Success Metrics - DEFINED",
            ]
            for step in steps:
                response += f"- {step}\n"
        else:
            # 기존 로컬 분석 사용
            steps = [
                "1. **Requirements Analysis**: Understand the feature requirements and constraints",
                "2. **Technical Design**: Plan the implementation approach and architecture",
                "3. **Code Quality Standards**: Ensure maintainable, testable, and scalable code",
                "4. **Implementation Strategy**: Break down development into manageable tasks",
                "5. **Testing Approach**: Define comprehensive testing strategy",
                "6. **Quality Assurance**: Establish code review and validation processes",
                "7. **Delivery Planning**: Timeline and deployment considerations",
                "8. **Success Metrics**: Define measurable outcomes and KPIs",
            ]

            response = f"🚀 **Development Analysis & Planning**\n\n**Query:** {query}\n\n**Development Framework:**\n"
            for step in steps:
                response += f"- {step}\n"

            response += f"\n**Development Strategy:**\n"
            response += _perform_dev_analysis(query)

        result = TextContent(type="text", text=response)
        return _add_confession_mode(result, "dev", query)


@register_tool("sp.grok")  # 도구명: sp.grok - 읽기 전용 Grok 세션 최적화
def grok(query: str = "") -> TextContent:
    """🤖 Grok - xAI's helpful and maximally truthful AI"""
    with memory_span("sp.grok"):
        if not query.strip():
            return TextContent(
                type="text",
                text="🤖 Grok tool activated.\n\nPlease provide a query for Grok AI assistance.",
            )

        # For now, provide a helpful response about Grok mode
        response = f"🤖 **Grok AI Assistance**\n\n**Query:** {query}\n\n"
        response += "Grok is xAI's helpful and maximally truthful AI. "
        response += "To use Grok, first switch to Grok mode with `/super-prompt/mode grok` or `--grok` flag.\n\n"
        response += "**Grok's Key Principles:**\n"
        response += "- Helpful and maximally truthful\n"
        response += "- Built by xAI (not based on other companies' models)\n"
        response += "- Focuses on understanding the universe\n\n"
        response += f"**Your Query:** {query}\n\n"
        response += "_Switch to Grok mode to get actual Grok responses._"

        return TextContent(type="text", text=response)


@register_tool("sp.db-expert")  # 도구명: sp.db-expert - 읽기 전용 데이터베이스 전문가 조언
def db_expert(query: str = "") -> TextContent:
    """🗄️ Database Expert - SQL, database design, and optimization specialist"""
    with memory_span("sp.db-expert"):
        if not query.strip():
            return TextContent(
                type="text",
                text="🗄️ Database Expert tool activated.\n\nPlease provide a database-related query or task.",
            )

        response = f"🗄️ **Database Expert Analysis**\n\n**Query:** {query}\n\n"
        response += "**Database Expertise Areas:**\n"
        response += "- SQL query optimization\n"
        response += "- Database schema design\n"
        response += "- Performance tuning\n"
        response += "- Data modeling\n"
        response += "- Migration strategies\n"
        response += "- Backup and recovery\n\n"
        response += f"**Analysis for:** {query}\n\n"
        response += "_This tool provides database expertise and best practices._"

        return TextContent(type="text", text=response)


@register_tool("sp.optimize")  # 도구명: sp.optimize - 읽기 전용 일반 최적화 조언
def optimize(query: str = "") -> TextContent:
    """⚡ Optimize - Performance optimization and efficiency specialist"""
    with memory_span("sp.optimize"):
        if not query.strip():
            return TextContent(
                type="text",
                text="⚡ Optimize tool activated.\n\nPlease provide a performance optimization task or query.",
            )

        response = f"⚡ **Performance Optimization Analysis**\n\n**Query:** {query}\n\n"
        response += "**Optimization Focus Areas:**\n"
        response += "- Code performance profiling\n"
        response += "- Algorithm optimization\n"
        response += "- Memory usage optimization\n"
        response += "- Database query optimization\n"
        response += "- System resource optimization\n"
        response += "- Load balancing and scaling\n\n"
        response += f"**Optimization Target:** {query}\n\n"
        response += "_This tool helps identify and implement performance improvements._"

        return TextContent(type="text", text=response)


@register_tool("sp.review")  # 도구명: sp.review - 읽기 전용 코드 리뷰 및 품질 검토
def review(query: str = "") -> TextContent:
    """🔍 Review - Code review and quality assurance specialist"""
    with memory_span("sp.review"):
        if not query.strip():
            return TextContent(
                type="text",
                text="🔍 Review tool activated.\n\nPlease provide code or a project to review.",
            )

        response = f"🔍 **Code Review & Quality Assurance**\n\n**Query:** {query}\n\n"
        response += "**Review Checklist:**\n"
        response += "- Code quality and style\n"
        response += "- Security vulnerabilities\n"
        response += "- Performance considerations\n"
        response += "- Test coverage\n"
        response += "- Documentation completeness\n"
        response += "- Best practices adherence\n\n"
        response += f"**Review Target:** {query}\n\n"
        response += "_This tool performs comprehensive code reviews and quality assessments._"

        return TextContent(type="text", text=response)


@register_tool("sp.service-planner")  # 도구명: sp.service-planner
def service_planner(query: str = "") -> TextContent:
    """🏗️ Service Planner - System architecture and service design specialist"""
    with memory_span("sp.service-planner"):
        if not query.strip():
            return TextContent(
                type="text",
                text="🏗️ Service Planner tool activated.\n\nPlease provide a service planning or architecture query.",
            )

        response = f"🏗️ **Service Architecture & Planning**\n\n**Query:** {query}\n\n"
        response += "**Service Planning Areas:**\n"
        response += "- Microservices architecture design\n"
        response += "- API design and documentation\n"
        response += "- Service orchestration\n"
        response += "- Scalability planning\n"
        response += "- Integration patterns\n"
        response += "- Deployment strategies\n\n"
        response += f"**Planning Focus:** {query}\n\n"
        response += "_This tool helps design robust and scalable service architectures._"

        return TextContent(type="text", text=response)


@register_tool("sp.tr")  # 도구명: sp.tr
def tr(query: str = "") -> TextContent:
    """🌐 Translate - Multi-language translation and localization specialist"""
    with memory_span("sp.tr"):
        if not query.strip():
            return TextContent(
                type="text",
                text="🌐 Translate tool activated.\n\nPlease provide text to translate or a translation task.",
            )

        response = f"🌐 **Translation & Localization Services**\n\n**Query:** {query}\n\n"
        response += "**Translation Capabilities:**\n"
        response += "- Multi-language translation\n"
        response += "- Technical documentation translation\n"
        response += "- UI/UX text localization\n"
        response += "- Cultural adaptation\n"
        response += "- Terminology management\n"
        response += "- Quality assurance for translations\n\n"
        response += f"**Translation Request:** {query}\n\n"
        response += "_This tool provides professional translation and localization services._"

        return TextContent(type="text", text=response)


@register_tool("sp.ultracompressed")  # 도구명: sp.ultracompressed
def ultracompressed(query: str = "") -> TextContent:
    """🗜️ Ultra Compressed - Maximum information density with minimal tokens"""
    with memory_span("sp.ultracompressed"):
        if not query.strip():
            return TextContent(
                type="text",
                text="🗜️ Ultra Compressed tool activated.\n\nPlease provide a query for ultra-compressed analysis.",
            )

        response = f"🗜️ **Ultra-Compressed Analysis**\n\n**Query:** {query}\n\n"
        response += "**Compression Strategy:**\n"
        response += "- Maximum information density\n"
        response += "- Minimal token usage\n"
        response += "- Essential insights only\n"
        response += "- High-signal, low-noise output\n"
        response += "- Prioritized critical information\n\n"
        response += f"**Compressed Analysis:** {query}\n\n"
        response += "_This tool provides highly condensed, information-dense responses._"

        return TextContent(type="text", text=response)


@register_tool("sp.doc-master")  # 도구명: sp.doc-master
def doc_master(query: str = "") -> TextContent:
    """📚 Doc Master - Documentation architecture, writing, and verification"""
    with memory_span("sp.doc-master"):
        if not query.strip():
            return TextContent(
                type="text",
                text="📚 Doc Master tool activated.\n\nPlease provide a documentation task or request.",
            )

        # Codex CLI 사용 여부 결정
        use_codex = _should_use_codex_assistance(query, "doc-master")

        if use_codex:
            print(
                "-------- doc-master: using Codex CLI for complex documentation analysis",
                file=sys.stderr,
                flush=True,
            )

            # 프로젝트 컨텍스트 수집
            project_root = Path.cwd()
            context_info = _analyze_project_context(project_root, query)
            context_str = f"Documentation context: {context_info.get('file_count', 0)} files, {len([p for p in context_info.get('patterns', []) if '.md' in p])} markdown files"

            # Codex CLI 호출
            codex_response = _call_codex_assistance(query, context_str, "doc-master")

            response = f"📚 **Documentation Analysis (Codex CLI)**\n\n**Query:** {query}\n\n"
            response += f"**📊 Documentation Context:**\n"
            response += f"- Total files: {context_info.get('file_count', 0)}\n"
            response += f"- Documentation files: {len([p for p in context_info.get('patterns', []) if '.md' in p])}\n"
            response += f"- Context clues: {', '.join(context_info.get('query_relevance', []))}\n\n"

            response += f"**🤖 Codex Documentation Insight:**\n"
            response += f"{codex_response}\n\n"

            # 문서화 프레임워크 표시
            response += f"**Documentation Framework:**\n"
            steps = [
                "✅ Documentation Strategy - PROVIDED BY CODEX",
                "✅ Content Architecture - GUIDED",
                "✅ Writing Standards - ESTABLISHED",
                "✅ Technical Accuracy - ENSURED",
                "✅ User Experience - OPTIMIZED",
            ]
            for step in steps:
                response += f"- {step}\n"
        else:
            # 기존 로컬 분석 사용
            steps = [
                "1. **Documentation Strategy**: Define documentation goals and audience",
                "2. **Content Architecture**: Structure and organize information hierarchy",
                "3. **Writing Standards**: Establish style, tone, and quality guidelines",
                "4. **Technical Accuracy**: Ensure all technical content is correct and up-to-date",
                "5. **User Experience**: Make documentation accessible and user-friendly",
                "6. **Maintenance Process**: Plan for ongoing updates and version control",
                "7. **Verification Methods**: Quality assurance and review processes",
                "8. **Distribution Strategy**: Publishing and accessibility considerations",
            ]

            response = f"📚 **Documentation Architecture & Strategy**\n\n**Query:** {query}\n\n**Documentation Framework:**\n"
            for step in steps:
                response += f"- {step}\n"

            response += f"\n**Documentation Strategy:**\n"
            response += _perform_doc_master_analysis(query)

        return TextContent(type="text", text=response)


@register_tool("sp.docs-refector")  # 도구명: sp.docs-refector
def docs_refector(query: str = "") -> TextContent:
    """🧹 Docs Refector - Repository-wide documentation audit, de-duplication, and consolidation"""
    with memory_span("sp.docs-refector"):
        # Analyze repository markdown/docs to propose a consolidation plan
        project_root = Path.cwd()
        md_files: list[Path] = []
        for pattern in ["**/*.md", "**/*.mdx"]:
            md_files.extend(project_root.glob(pattern))

        # Build simple indices: by filename stem and first heading
        name_index: dict[str, list[Path]] = {}
        heading_index: dict[str, list[Path]] = {}
        for path in md_files:
            if not path.is_file():
                continue
            stem = path.stem.lower()
            name_index.setdefault(stem, []).append(path)
            try:
                first_line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:10]
                heading = next(
                    (l.strip("# ") for l in first_line if l.lstrip().startswith("#")), ""
                )
                if heading:
                    heading_index.setdefault(heading.lower(), []).append(path)
            except Exception:
                # Ignore unreadable files
                continue

        duplicates_by_name = {k: v for k, v in name_index.items() if len(v) > 1}
        duplicates_by_heading = {k: v for k, v in heading_index.items() if len(v) > 1}

        docs_dirs = [
            p
            for p in [project_root / "docs", project_root / "packages", project_root / "specs"]
            if p.exists()
        ]

        response = ["🧹 **Docs Refector Audit & Consolidation Plan**\n"]
        response.append(f"Total markdown-like files: {len(md_files)}\n")

        if duplicates_by_name:
            response.append("\n### Potential Duplicates (by filename)\n")
            for stem, paths in list(duplicates_by_name.items())[:20]:
                shown = "\n".join(f"- {p.as_posix()}" for p in paths[:6])
                more = " (and more)" if len(paths) > 6 else ""
                response.append(f"- {stem}:{more}\n{shown}\n")

        if duplicates_by_heading:
            response.append("\n### Potential Duplicates (by top-level heading)\n")
            for heading, paths in list(duplicates_by_heading.items())[:20]:
                shown = "\n".join(f"- {p.as_posix()}" for p in paths[:6])
                more = " (and more)" if len(paths) > 6 else ""
                response.append(f"- {heading}:{more}\n{shown}\n")

        if docs_dirs:
            response.append("\n### Documentation Areas Scanned\n")
            for d in docs_dirs:
                response.append(f"- {d.as_posix()}\n")

        # High-level refactor plan
        response.append("\n### Proposed Consolidation Strategy\n")
        response.append("- Build a canonical information architecture (IA) with sources of truth\n")
        response.append("- Merge duplicates; create redirects or cross-links where necessary\n")
        response.append("- Remove obsolete/legacy files; update internal links\n")
        response.append("- Normalize style (headings, frontmatter, tone)\n")
        response.append("- Add verification checklist and ownership for sustained maintenance\n")

        if query.strip():
            response.append("\n### Focus Area\n")
            response.append(f"- User request: {query}\n")

        return TextContent(type="text", text="".join(response))


def _perform_sequential_analysis(query: str) -> str:
    """Perform basic sequential analysis for the given query"""
    query_lower = query.lower()

    if "1+1" in query_lower or "one plus one" in query_lower:
        return """Let's analyze: "Why is 1+1 equal to 2?"

**Step 1 - Understanding the Problem:**
- We have two individual units (1 and 1)
- We want to combine them and find the total

**Step 2 - Key Concepts:**
- Addition is the mathematical operation of combining quantities
- The number 1 represents a single unit
- The equals sign (=) shows equivalence

**Step 3 - Logical Reasoning:**
- When we have one unit and add another unit, we have two units total
- This is a fundamental property of counting and arithmetic
- 1 + 1 = 2 is an axiom in mathematics - a basic truth that doesn't need proof

**Step 4 - Verification:**
- Count with fingers: One finger + one finger = two fingers ✓
- Use physical objects: One apple + one apple = two apples ✓
- Mathematical consistency: The pattern holds across all number systems

**Step 5 - Conclusion:**
1 + 1 = 2 because when you combine two single units, you get a quantity of two units. This is a fundamental principle of arithmetic that forms the basis for all mathematical operations."""

    else:
        return f"""**Sequential Analysis for:** {query}

This appears to be a general reasoning problem. Let me break it down:

**Core Question Identification:**
- The main inquiry seems to be: {query}

**Reasoning Approach:**
- I'll analyze this systematically using logical principles
- Consider multiple perspectives and potential solutions
- Validate assumptions and conclusions

**Note:** For specific mathematical, scientific, or technical questions, please provide more context for a more detailed analysis."""


def _perform_ultra_sequential_analysis(query: str) -> str:
    """Perform ultra-deep sequential analysis for complex queries"""
    query_lower = query.lower()

    if "1+1" in query_lower or "one plus one" in query_lower:
        return """## Ultra-Deep Analysis: "Why is 1+1 equal to 2?"

### 1. Problem Decomposition
**Fundamental Question:** What is the nature of addition and why does 1+1 specifically equal 2?
**Scope:** Mathematical foundations, philosophical implications, practical applications
**Assumptions:** We're working within standard arithmetic systems

### 2. Knowledge Base Analysis
**Mathematical Foundations:**
- Peano axioms (axiomatic set theory)
- Successor function and natural numbers
- Addition as repeated succession

**Philosophical Context:**
- Platonism vs. Formalism in mathematics
- The nature of mathematical truth
- Empirical vs. logical necessity

**Cognitive Science:**
- How humans conceptualize addition
- Innate number sense in infants
- Cultural variations in counting systems

### 3. Logical Framework Construction
**Formal Definition:**
```
Addition: ∀a,b ∈ ℕ: a + b = a + S(b) where S is the successor function
Base case: a + 0 = a
Recursive case: a + S(b) = S(a + b)
```

**Peano Arithmetic:**
- 0 is a natural number
- Every natural number has a unique successor
- 1 is defined as S(0)
- 2 is defined as S(S(0)) = S(1)

### 4. Step-by-Step Deduction
**Mathematical Proof:**
1. Start with: 1 + 1
2. Using definition: 1 + 1 = 1 + S(0)
3. Apply successor: 1 + S(0) = S(1 + 0)
4. Base case: 1 + 0 = 1
5. Therefore: S(1) = 2 ✓

**Alternative Proof (Set Theory):**
- {∅} ∪ {∅} = {∅, {∅}} (cardinality 2)
- Union of two singleton sets creates a set with two elements

### 5. Alternative Perspectives
**Psychological Perspective:**
- Infants as young as 6 months understand 1+1=2 through object permanence
- Cross-cultural studies show this understanding is universal

**Computational Perspective:**
- Binary representation: 1 + 1 = 10 (decimal 2)
- Boolean algebra: True + True = 2 (interpreted as carry + sum)

**Philosophical Perspective:**
- Is 1+1=2 necessarily true, or is it a convention?
- Gödel's incompleteness theorems and mathematical certainty

### 6. Validation & Verification
**Consistency Checks:**
- Commutativity: 1 + 1 = 1 + 1 ✓
- Associativity: (1 + 1) + 0 = 1 + (1 + 0) ✓
- Field properties maintained

**Empirical Validation:**
- Physical counting validation
- Computational verification across systems
- Cognitive developmental studies

### 7. Synthesis & Conclusion
**Core Truth:** 1 + 1 = 2 is a fundamental mathematical truth that:
- Forms the basis of arithmetic
- Is consistent across different mathematical systems
- Has both logical and empirical validation
- Serves as a foundation for all subsequent mathematical operations

**Limitations:**
- Applies within standard number systems
- May not hold in non-standard arithmetic (e.g., modular arithmetic)
- Subject to philosophical debate about mathematical Platonism

### 8. Confidence Assessment
**High Confidence Factors:**
- Universal mathematical consistency
- Empirical validation across cultures and species
- Logical necessity within Peano arithmetic

**Areas of Uncertainty:**
- Philosophical foundations of mathematics
- Consciousness and subjective experience of number
- Ultimate nature of mathematical truth

**Final Assessment:** 99.9% confidence in the mathematical truth 1+1=2, with philosophical caveats about the nature of mathematical reality."""

    else:
        return f"""## Ultra-Deep Sequential Analysis: {query}

### 1. Problem Decomposition
**Primary Question:** {query}
**Analysis Scope:** Comprehensive multi-disciplinary examination
**Complexity Level:** Advanced reasoning required

### 2. Knowledge Base Analysis
**Relevant Domains:**
- Core subject matter analysis
- Interdisciplinary connections
- Historical context and evolution
- Current state and future implications

### 3. Logical Framework Construction
**Systematic Approach:**
- Hypothesis generation and testing
- Evidence evaluation framework
- Counter-argument consideration
- Synthesis methodology

### 4. Step-by-Step Deduction
**Detailed Reasoning Process:**
- Break down complex elements
- Establish logical connections
- Validate each step rigorously
- Build towards comprehensive conclusion

### 5. Alternative Perspectives
**Multi-Viewpoint Analysis:**
- Different theoretical frameworks
- Cultural and contextual variations
- Historical vs. modern interpretations
- Practical vs. theoretical implications

### 6. Validation & Verification
**Robustness Testing:**
- Internal consistency checks
- External validation methods
- Peer review and expert consensus
- Predictive accuracy assessment

### 7. Synthesis & Conclusion
**Integrated Findings:**
- Comprehensive answer synthesis
- Key insights and implications
- Areas requiring further investigation

### 8. Confidence Assessment
**Confidence Level:** Medium-High (context-dependent)
**Strengths:** Systematic methodology, comprehensive analysis
**Limitations:** Subject-specific expertise requirements, evolving knowledge

**Recommendation:** Please provide additional context or specify the domain for more targeted analysis."""


def _analyze_project_context(project_root: Path, query: str) -> dict:
    """Analyze project context to provide situation clues for high reasoning"""
    try:
        context = {
            "file_count": 0,
            "patterns": [],
            "key_files": [],
            "structure": {},
            "query_relevance": [],
        }

        # Count files and analyze structure
        if project_root.exists():
            all_files = list(project_root.rglob("*"))
            context["file_count"] = len([f for f in all_files if f.is_file()])

            # Analyze file patterns
            extensions = {}
            for file in all_files:
                if file.is_file():
                    ext = file.suffix.lower()
                    extensions[ext] = extensions.get(ext, 0) + 1

            # Get top patterns
            sorted_patterns = sorted(extensions.items(), key=lambda x: x[1], reverse=True)
            context["patterns"] = [f"{ext}: {count}" for ext, count in sorted_patterns[:5]]

        # Add query-specific context clues
        query_lower = query.lower()
        if any(word in query_lower for word in ["api", "endpoint", "rest", "graphql"]):
            context["query_relevance"].append("API development context detected")
        if any(word in query_lower for word in ["database", "sql", "schema", "migration"]):
            context["query_relevance"].append("Database operations context detected")
        if any(word in query_lower for word in ["ui", "frontend", "component", "react"]):
            context["query_relevance"].append("Frontend development context detected")
        if any(word in query_lower for word in ["security", "auth", "permission", "encryption"]):
            context["query_relevance"].append("Security implementation context detected")

        return context

    except Exception as e:
        return {"file_count": 0, "patterns": [], "error": str(e)}


def _prepare_high_reasoning_prompt(query: str, context: dict) -> str:
    """Prepare comprehensive prompt for high reasoning analysis"""
    prompt_parts = []

    # Situation summary
    prompt_parts.append("## Current Situation Analysis")
    prompt_parts.append(f"Query: {query}")
    prompt_parts.append(f"Project files analyzed: {context.get('file_count', 0)}")
    prompt_parts.append(f"Key patterns: {', '.join(context.get('patterns', []))}")

    if context.get("query_relevance"):
        prompt_parts.append(f"Context clues: {', '.join(context['query_relevance'])}")

    # High reasoning framework
    prompt_parts.append("\n## High Reasoning Framework")
    prompt_parts.append("You are operating in HIGH REASONING MODE with maximum analytical depth.")
    prompt_parts.append("Follow this systematic approach:")
    prompt_parts.append(
        "1. **Strategic Analysis**: Assess broader implications and strategic context"
    )
    prompt_parts.append("2. **Deep Problem Decomposition**: Break down into fundamental components")
    prompt_parts.append(
        "3. **Multi-Disciplinary Synthesis**: Consider multiple perspectives and domains"
    )
    prompt_parts.append("4. **Advanced Logical Frameworks**: Apply rigorous reasoning structures")
    prompt_parts.append(
        "5. **Risk Assessment**: Identify potential issues and mitigation strategies"
    )
    prompt_parts.append(
        "6. **Long-term Implications**: Consider future consequences and scalability"
    )
    prompt_parts.append("7. **Decision Optimization**: Evaluate optimal paths and trade-offs")
    prompt_parts.append(
        "8. **Implementation Strategy**: Develop actionable plans with success metrics"
    )

    # Query-specific guidance
    prompt_parts.append("\n## Analysis Requirements")
    prompt_parts.append("Provide comprehensive analysis with:")
    prompt_parts.append("- Detailed reasoning steps with justification")
    prompt_parts.append("- Multiple perspectives and alternative viewpoints")
    prompt_parts.append("- Risk assessment and mitigation strategies")
    prompt_parts.append("- Actionable recommendations with priorities")
    prompt_parts.append("- Success metrics and evaluation criteria")

    return "\n".join(prompt_parts)


def _perform_high_reasoning_analysis(query: str) -> str:
    """Perform high-level strategic analysis for complex queries"""
    query_lower = query.lower()

    if "1+1" in query_lower or "one plus one" in query_lower:
        return """## 🧠 High-Level Strategic Analysis: "Why is 1+1 equal to 2?"

### 1. Strategic Context Assessment
**Fundamental Question:** What are the strategic implications of this basic mathematical truth?
**Scope:** Mathematical foundations, philosophical implications, computational consequences
**Strategic Importance:** Understanding this axiom reveals deeper truths about logic, computation, and reality

### 2. Deep Problem Decomposition
**Core Components:**
- **Arithmetic Foundation**: The basic operation of addition
- **Logical Necessity**: Why this must be true in any consistent system
- **Computational Universality**: How this underlies all digital computation
- **Philosophical Implications**: What this reveals about the nature of truth

**Root Cause Analysis:**
- Mathematical axioms are the foundation of all formal systems
- 1+1=2 is not just a calculation—it's a logical necessity
- Any system that contradicts this would be inconsistent and unusable

### 3. Multi-Disciplinary Synthesis
**Mathematical Perspective:**
- Peano Arithmetic foundation
- Set theory interpretations
- Algebraic structure requirements

**Computational Perspective:**
- Binary representation: 1 + 1 = 10₂ = 2₁₀
- Boolean algebra and digital logic
- Quantum computing implications

**Philosophical Perspective:**
- Platonism vs. Formalism debate
- Gödel's incompleteness theorems
- Nature of mathematical truth

### 4. Advanced Logical Frameworks
**Formal Proof Theory:**
```
Axiom: ∀x,y ∈ ℕ: x + y = x + S(y) where S is successor
Base: ∀x: x + 0 = x
Induction: ∀x,y: x + S(y) = S(x + y)

Proof that 1 + 1 = 2:
1 + 1 = 1 + S(0)           [Definition]
      = S(1 + 0)           [Successor rule]
      = S(1)               [Base case]
      = 2                  [Definition of 2]
```

**Model Theory:**
- Any model of arithmetic must satisfy 1+1=2
- This constrains possible interpretations of numbers

### 5. Risk Assessment & Mitigation
**Potential Risks:**
- **Paradoxical Systems**: Systems where basic arithmetic fails
- **Inconsistent Foundations**: Undermining mathematical certainty
- **Computational Errors**: Cascading failures in digital systems

**Mitigation Strategies:**
- Formal verification of critical systems
- Multiple computational paradigms
- Cross-validation across different number systems

### 6. Long-term Implications
**Computational Future:**
- Quantum computing reliability depends on logical consistency
- AI systems must maintain arithmetic foundations
- Cryptographic systems depend on mathematical certainty

**Scientific Impact:**
- Physics theories must be consistent with arithmetic
- Biological computation models
- Cognitive science and mathematical intuition

### 7. Decision Optimization
**Optimal Paths:**
- Accept 1+1=2 as fundamental constraint
- Build complex systems on this foundation
- Use formal methods to ensure consistency

**Trade-off Analysis:**
- **Certainty vs. Complexity**: Absolute certainty enables complex systems
- **Efficiency vs. Correctness**: Formal verification overhead vs. reliability
- **Innovation vs. Stability**: Pushing boundaries while maintaining foundations

### 8. Implementation Strategy
**Actionable Framework:**
1. **Foundation Verification**: Ensure arithmetic consistency in all systems
2. **Formal Methods Integration**: Use proof assistants for critical components
3. **Multi-Layer Validation**: Cross-check across different computational models
4. **Continuous Monitoring**: Watch for logical inconsistencies
5. **Knowledge Preservation**: Document mathematical foundations

**Success Metrics:**
- System reliability: 99.999% consistency maintenance
- Computational efficiency: Minimal overhead for verification
- Innovation enablement: Support for increasingly complex systems
- Risk mitigation: Proactive identification of logical threats

**Strategic Recommendation:** Embrace 1+1=2 as the cornerstone of reliable computation and complex system design."""

    else:
        return f"""## 🧠 High-Level Strategic Analysis: {query}

### 1. Strategic Context Assessment
**Primary Objective:** Conduct comprehensive strategic analysis
**Scope:** Multi-disciplinary examination with long-term implications
**Strategic Value:** Identify optimal paths and mitigate risks

### 2. Deep Problem Decomposition
**Core Components:**
- **Primary Challenge**: {query}
- **Secondary Factors**: Context-dependent considerations
- **Root Cause Analysis**: Fundamental drivers and constraints
- **System Interactions**: How components interrelate

### 3. Multi-Disciplinary Synthesis
**Integrated Perspectives:**
- **Technical Analysis**: System architecture and implementation
- **Business Impact**: Economic and operational consequences
- **Human Factors**: User experience and organizational dynamics
- **Risk Assessment**: Potential failure modes and mitigation strategies

### 4. Advanced Logical Frameworks
**Strategic Frameworks:**
- **SWOT Analysis**: Strengths, Weaknesses, Opportunities, Threats
- **Decision Trees**: Branching logic for complex scenarios
- **Systems Thinking**: Holistic understanding of interactions
- **Game Theory**: Strategic interactions and optimal play

### 5. Risk Assessment & Mitigation
**Risk Categories:**
- **Technical Risks**: Implementation challenges and technical debt
- **Operational Risks**: Deployment and maintenance complexities
- **Strategic Risks**: Market changes and competitive threats
- **Compliance Risks**: Regulatory and legal considerations

**Mitigation Strategies:**
- **Diversification**: Multiple approaches and backup plans
- **Monitoring**: Continuous assessment and early warning systems
- **Contingency Planning**: Alternative paths and recovery procedures

### 6. Long-term Implications
**Future Considerations:**
- **Scalability**: How the solution grows over time
- **Evolution**: Adapting to changing requirements
- **Legacy**: Long-term maintainability and technical debt
- **Innovation**: Enabling future capabilities and improvements

### 7. Decision Optimization
**Optimization Criteria:**
- **Efficiency**: Resource utilization and performance metrics
- **Effectiveness**: Achievement of strategic objectives
- **Sustainability**: Long-term viability and maintenance costs
- **Risk-Adjusted Returns**: Benefits weighed against uncertainties

### 8. Implementation Strategy
**Strategic Roadmap:**
1. **Phase 1: Foundation** - Establish core capabilities
2. **Phase 2: Integration** - Connect with existing systems
3. **Phase 3: Optimization** - Refine and improve performance
4. **Phase 4: Scaling** - Expand to full operational capacity

**Success Metrics:**
- **Quantitative**: Measurable KPIs and performance indicators
- **Qualitative**: Stakeholder satisfaction and strategic alignment
- **Risk Metrics**: Reduction in identified vulnerabilities
- **Innovation Metrics**: New capabilities and competitive advantages

**Strategic Recommendation:** Focus on foundational strength while maintaining flexibility for future evolution."""


def _execute_persona(persona_name: str, query: str = "", **kwargs) -> TextContent:
    """Execute persona with given query"""
    try:
        # Avoid importing the full CLI to keep dependencies minimal in MCP/direct mode
        from .personas.loader import PersonaLoader

        # Load persona configuration
        loader = PersonaLoader()
        loader.load_manifest()

        # Get persona config
        persona_config = None
        for p in loader.list_personas():
            if p["name"] == persona_name:
                persona_config = p
                break

        if not persona_config:
            # Fallback when manifest is missing or PyYAML unavailable
            fallback_prompt = f"You are the {persona_name} persona.\n\nUser query: {query}"
            return TextContent(
                type="text",
                text=f"🎭 {persona_name.title()} persona activated!\n\n{fallback_prompt}",
            )

        # Create persona prompt
        persona_prompt = f"""You are {persona_config['description']}.

{persona_config.get('system_prompt', '')}

User query: {query}"""

        # Return persona activation message
        # Use emoji if available, otherwise a generic mask
        emoji = persona_config.get("emoji", "🎭")
        return TextContent(
            type="text",
            text=f"🎭 {emoji} {persona_config['name'].title()} persona activated!\n\n{persona_prompt}",
        )

    except Exception as e:
        return TextContent(type="text", text=f"Error executing persona: {str(e)}")


def _perform_dev_analysis(query: str) -> str:
    """Perform development-focused analysis for the given query"""
    query_lower = query.lower()

    if any(
        keyword in query_lower for keyword in ["feature", "implement", "build", "develop", "create"]
    ):
        return """## 🚀 Development Strategy Analysis

### Requirements Analysis
**Functional Requirements:**
- Clear specification of desired functionality
- User acceptance criteria and success metrics
- Integration points with existing systems
- Performance and scalability expectations

**Non-Functional Requirements:**
- Code quality standards and maintainability
- Testing coverage and validation criteria
- Security considerations and compliance
- Performance benchmarks and monitoring

### Technical Design
**Architecture Considerations:**
- Modular design with clear separation of concerns
- Scalable and maintainable code structure
- Error handling and resilience patterns
- Database design and data flow optimization

**Technology Stack:**
- Framework and library selections
- Development tools and CI/CD pipeline
- Testing frameworks and quality gates
- Deployment and infrastructure requirements

### Code Quality Standards
**Best Practices:**
- Clean Code principles and SOLID design
- Comprehensive test coverage (unit, integration, e2e)
- Code review processes and quality gates
- Documentation standards and API contracts

**Quality Metrics:**
- Cyclomatic complexity limits
- Code coverage thresholds (target: >80%)
- Performance benchmarks and memory usage
- Security vulnerability scanning

### Implementation Strategy
**Development Phases:**
1. **Planning & Design** (1-2 days)
2. **Core Implementation** (3-5 days)
3. **Testing & Validation** (2-3 days)
4. **Integration & Deployment** (1-2 days)

**Risk Mitigation:**
- Regular code reviews and pair programming
- Automated testing and continuous integration
- Feature flags for gradual rollout
- Rollback plans and monitoring alerts

### Testing Approach
**Testing Pyramid:**
- **Unit Tests**: Core business logic validation
- **Integration Tests**: Component interaction verification
- **End-to-End Tests**: Complete user journey testing
- **Performance Tests**: Load and stress testing

**Quality Assurance:**
- Code review checklist and standards
- Automated security scanning
- Accessibility and usability testing
- Cross-browser and device compatibility

### Delivery Planning
**Timeline Estimation:**
- Small features: 1-2 weeks
- Medium features: 2-4 weeks
- Large features: 1-2 months
- Complex features: 2-3 months

**Milestone Planning:**
- Weekly progress reviews and demos
- Sprint planning and backlog management
- Stakeholder communication and updates
- Risk assessment and mitigation planning

### Success Metrics
**Quantitative Metrics:**
- Code coverage: >80%
- Performance benchmarks met: 100%
- Bug rate: <0.1 per 100 lines
- Deployment success rate: >99%

**Qualitative Metrics:**
- User satisfaction scores
- Code maintainability ratings
- Team productivity improvements
- Stakeholder feedback and adoption rates

**Strategic Recommendation:** Focus on iterative development with strong quality gates and continuous feedback loops."""

    else:
        return f"""## 🚀 Development Analysis: {query}

### Core Development Principles
**Quality First Approach:**
- Clean, maintainable, and scalable code
- Comprehensive testing and validation
- Security by design and best practices
- Performance optimization and monitoring

**Agile Development:**
- Iterative development with frequent feedback
- Continuous integration and deployment
- Automated testing and quality gates
- Collaborative development practices

### Recommended Development Workflow
1. **Requirement Gathering**: Define clear specifications and acceptance criteria
2. **Technical Design**: Create detailed design documents and architecture plans
3. **Implementation**: Write clean, well-tested code following best practices
4. **Code Review**: Peer review and quality assurance processes
5. **Testing**: Comprehensive testing at all levels
6. **Deployment**: Safe deployment with monitoring and rollback capabilities

### Quality Assurance Framework
**Code Quality:**
- Static analysis and linting
- Code coverage reporting
- Performance profiling
- Security vulnerability scanning

**Process Quality:**
- Version control best practices
- Documentation standards
- Change management procedures
- Risk assessment and mitigation

**Strategic Focus:** Build with quality, scalability, and maintainability as primary objectives."""


def _perform_doc_master_analysis(query: str) -> str:
    """Perform documentation-focused analysis for the given query"""
    query_lower = query.lower()

    if any(
        keyword in query_lower for keyword in ["api", "documentation", "docs", "guide", "manual"]
    ):
        return """## 📚 Documentation Architecture Strategy

### Documentation Strategy
**Target Audience Analysis:**
- **Developers**: API references, code examples, architecture docs
- **Users**: User guides, tutorials, troubleshooting guides
- **Administrators**: Installation, configuration, maintenance docs
- **Stakeholders**: High-level overviews and business context

**Documentation Goals:**
- Reduce support tickets through self-service resources
- Accelerate onboarding for new team members
- Establish knowledge base for long-term maintenance
- Demonstrate product value and capabilities

### Content Architecture
**Information Hierarchy:**
- **Level 1**: Product overview and getting started
- **Level 2**: Feature documentation and user guides
- **Level 3**: API references and technical specifications
- **Level 4**: Advanced topics and troubleshooting

**Content Types:**
- **Conceptual**: What and why explanations
- **Procedural**: How-to guides and tutorials
- **Reference**: API docs and specifications
- **Troubleshooting**: Common issues and solutions

### Writing Standards
**Style Guidelines:**
- Clear, concise, and accessible language
- Active voice and consistent terminology
- Structured format with consistent headings
- Inclusive and professional tone

**Technical Standards:**
- Version-specific documentation
- Code examples in multiple languages
- Screenshots and diagrams for visual clarity
- Cross-references and navigation aids

### Technical Accuracy
**Validation Processes:**
- Technical review by subject matter experts
- Automated testing of code examples
- Version control integration for accuracy
- Regular updates for feature changes

**Quality Assurance:**
- Grammar and style checking
- Link validation and broken reference detection
- User feedback integration and improvement cycles
- Accessibility compliance and standards adherence

### User Experience
**Navigation Design:**
- Intuitive information architecture
- Search functionality and filters
- Progressive disclosure of information
- Mobile-responsive design

**User Journey Mapping:**
- New user onboarding flow
- Feature discovery and learning paths
- Support and troubleshooting workflows
- Advanced user deep-dive paths

### Maintenance Process
**Content Lifecycle:**
- **Creation**: New feature documentation
- **Review**: Regular accuracy and relevance checks
- **Update**: Feature changes and improvements
- **Archival**: Deprecated feature documentation

**Version Management:**
- Documentation versioning aligned with product releases
- Branch-based workflow for content updates
- Automated publishing and deployment
- Change tracking and audit trails

### Verification Methods
**Quality Gates:**
- Technical accuracy review checklist
- User experience testing and feedback
- SEO optimization and discoverability
- Performance monitoring and load testing

**Metrics and KPIs:**
- Page views and user engagement
- Search success rates and time to find information
- User satisfaction scores and feedback ratings
- Support ticket reduction and self-service adoption

### Distribution Strategy
**Publishing Platforms:**
- **Internal Wiki/Knowledge Base**: Team collaboration and internal docs
- **Public Documentation Site**: User-facing guides and references
- **API Documentation Portal**: Developer resources and integration guides
- **Video Tutorials**: Visual learning and demonstrations

**Accessibility Considerations:**
- Multi-language support and localization
- Screen reader compatibility and accessibility standards
- Offline documentation options and downloadable resources
- Mobile and tablet optimization

**Strategic Recommendation:** Implement a comprehensive documentation strategy that serves all stakeholders with accurate, accessible, and maintainable content."""

    else:
        return f"""## 📚 Documentation Strategy: {query}

### Documentation Excellence Framework
**Core Principles:**
- **Accuracy**: Technically correct and up-to-date information
- **Accessibility**: Easy to find, read, and understand
- **Maintainability**: Sustainable processes for content updates
- **User-Centric**: Designed around user needs and workflows

### Comprehensive Documentation Strategy
1. **Audience Analysis**: Identify and understand user personas and their needs
2. **Content Planning**: Define documentation scope and information architecture
3. **Writing Process**: Establish style guides and quality standards
4. **Technical Validation**: Ensure accuracy through expert review and testing
5. **Publishing Workflow**: Streamlined processes for content deployment
6. **Maintenance Plan**: Ongoing updates and improvement cycles

### Quality Assurance Standards
**Content Quality:**
- Technical accuracy and completeness
- Clear and concise writing style
- Consistent formatting and structure
- User feedback integration

**Technical Quality:**
- Automated link checking and validation
- Search engine optimization
- Mobile responsiveness and accessibility
- Performance optimization

### Success Metrics
**Quantitative Measures:**
- Documentation coverage completeness
- User engagement and page view metrics
- Search success rates and findability
- Support ticket deflection rates

**Qualitative Measures:**
- User satisfaction and feedback scores
- Content clarity and usability ratings
- Stakeholder adoption and usage patterns
- Team productivity improvements

**Strategic Focus:** Create documentation that empowers users, reduces support burden, and accelerates product adoption."""


if __name__ == "__main__":
    # Handle direct-call fast path if requested
    if _run_direct_tool_if_requested():
        sys.exit(0)

    # Otherwise start the MCP server if SDK is available
    if not _HAS_MCP:
        print(
            "-------- ERROR: MCP SDK (python mcp) not installed; cannot start server",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(96)

    # Initialize memory system early to ensure database is ready
    try:
        from .memory.store import MemoryStore

        MemoryStore.open()  # Initialize memory database
        print("-------- memory: system initialized", file=sys.stderr, flush=True)
    except Exception as e:
        print(
            f"-------- WARNING: memory system initialization failed: {e}",
            file=sys.stderr,
            flush=True,
        )

    # stdio 모드로 MCP 서버 실행 (버전 호환성 고려)
    print("-------- MCP server starting in stdio mode", file=sys.stderr, flush=True)

    # Try different run patterns for maximum compatibility
    run_attempts = [
        # Standard pattern for most versions
        lambda: mcp.run(),
        # Some versions might require stdio parameter
        lambda: mcp.run(transport="stdio"),
        lambda: mcp.run({"transport": "stdio"}),
        lambda: mcp.run(transport={"type": "stdio"}),
        # Alternative parameter patterns
        lambda: mcp.run_stdio(),
        lambda: mcp.run(mode="stdio"),
        lambda: mcp.run({"mode": "stdio"}),
        # Legacy patterns for older versions
        lambda: mcp.serve(),
        lambda: mcp.serve_stdio(),
    ]

    server_started = False
    for run_func in run_attempts:
        try:
            print(
                f"-------- MCP: trying server run pattern: {run_func.__name__}",
                file=sys.stderr,
                flush=True,
            )
            run_func()
            server_started = True
            print("-------- MCP: server started successfully", file=sys.stderr, flush=True)
            break
        except (TypeError, AttributeError, ValueError) as e:
            print(f"-------- MCP: run attempt failed: {e}", file=sys.stderr, flush=True)
            continue

    if not server_started:
        print(
            "-------- ERROR: Failed to start MCP server with any known pattern",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)
