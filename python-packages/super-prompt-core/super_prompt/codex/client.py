# packages/core-py/super_prompt/codex/client.py
"""Codex CLI integration helpers for Super Prompt."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

# Markers returned by the Codex CLI when authentication is missing
_LOGIN_MARKERS = (
    "login",
    "authenticate",
    "authorization",
    "sign in",
    "no active session",
    "api key",
    "로그인",
)

_LOGIN_REQUIRED_MESSAGE = """❌ **Codex 로그인 필요**\n\n터미널에서 `codex login`을 실행해 인증을 완료한 뒤 다시 시도해주세요.\n인증이 끝나기 전까지 고급 추론 계획은 계속할 수 없습니다."""

_INSTALL_TIMEOUT_MESSAGE = """❌ **Codex CLI 설치 실패**\n\n`sudo npm install -g @openai/codex@latest` 명령이 완료되지 않았습니다.\n\n1. Node.js와 npm이 설치되어 있는지 확인하세요.\n2. 관리자 권한이 필요한 경우 터미널에서 직접 명령을 실행하세요.\n3. 설치가 완료된 뒤 다시 시도해주세요."""


@dataclass
class CodexUnavailableError(Exception):
    """Raised when Codex dependencies are missing or unavailable."""

    error_type: str
    message: str
    hint: str

    def to_dict(self) -> Dict[str, str]:
        return {"error": f"{self.error_type}: {self.message}", "hint": self.hint}


def _ensure_codex_cli_latest(timeout: int = 240) -> Optional[str]:
    """Install or update the Codex CLI to the latest version via npm."""

    if shutil.which("npm") is None:
        return (
            "❌ **npm을 찾을 수 없습니다**\n\n"
            "Node.js와 npm을 먼저 설치한 뒤 다시 시도해주세요.\n"
            "macOS 예시: `brew install node`"
        )

    try:
        proc = subprocess.run(
            ["sudo", "npm", "install", "-g", "@openai/codex@latest"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return _INSTALL_TIMEOUT_MESSAGE
    except FileNotFoundError:
        return (
            "❌ **npm 실행 실패**\n\n"
            "PATH에 npm이 없거나 손상되었습니다. Node.js 재설치를 검토해주세요."
        )
    except Exception as error:  # pragma: no cover - defensive branch
        return f"❌ **Codex CLI 설치 오류**\n\n{error}"

    if proc.returncode != 0:
        details = proc.stderr.strip() or proc.stdout.strip() or "원인을 알 수 없는 오류"
        if "password" in details.lower():
            return (
                "❌ **sudo 권한 필요**\n\n"
                "자동 설치에 실패했습니다. 터미널에서 직접 다음 명령을 실행해주세요:\n"
                "`sudo npm install -g @openai/codex@latest`"
            )
        return (
            "❌ **Codex CLI 설치 실패**\n\n"
            f"{details}\n\n"
            "터미널에서 `sudo npm install -g @openai/codex@latest`를 직접 실행해 문제를 해결한 뒤 다시 시도해주세요."
        )

    if shutil.which("codex") is None:
        return (
            "❌ **codex 실행 파일을 찾을 수 없습니다**\n\n"
            "글로벌 설치가 성공적으로 완료되지 않았습니다. 설치 명령을 수동으로 다시 실행해 주세요."
        )

    return None


def _sanitize_prompt(prompt: str, max_chars: int = 15000) -> str:
    """Trim excessively long prompts to avoid CLI argument limits."""

    prompt = prompt.strip()
    if len(prompt) <= max_chars:
        return prompt
    return prompt[: max_chars - 80] + "\n\n[context truncated to fit Codex CLI input limits]"


def _build_high_prompt(query: str, persona: str, context: str) -> str:
    """Compose the high-effort reasoning prompt for Codex."""

    persona = persona or "high"
    clean_query = (query or "").strip() or "No user query provided."
    context_block = (context or "").strip() or "No repository context collected."
    if len(context_block) > 6000:
        context_block = context_block[:6000] + "\n\n[context truncated]"

    instructions = textwrap.dedent(
        f"""
        You are the Super Prompt high-effort planner operating under persona `{persona}`.
        Analyse the repository context and craft a detailed execution plan before any coding begins.

        Return Markdown with these sections:
        1. PLAN — Numbered steps, each with intent, key files, and expected outputs.
        2. RISKS — Bullet list of open questions, uncertainties, or external dependencies.
        3. VALIDATION — Commands or checks to confirm the work (tests, linters, playbooks).
        4. FOLLOW-UPS — MCP commands or human actions required after completing the plan.

        Incorporate repository constraints, AGENTS.md guidance, and persona expectations.
        Stay factual, avoid speculation, and keep the plan executable by other MCP tools.
        """
    ).strip()

    return textwrap.dedent(
        f"""
        {instructions}

        [USER QUERY]
        {clean_query}

        [REPOSITORY CONTEXT]
        {context_block}
        """
    ).strip()


def _run_codex_exec_high(prompt: str) -> str:
    """Execute the Codex CLI with high reasoning configuration."""

    sanitized = _sanitize_prompt(prompt)
    command = [
        "codex",
        "exec",
        "-c",
        'model_reasoning_effort="high"',
        "-c",
        "reasoning_summaries=false",
        "--sandbox",
        "read-only",
        sanitized,
    ]

    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return (
            "❌ **Codex 실행 시간 초과**\n\n"
            "프롬프트가 너무 크거나 네트워크가 지연되고 있습니다. 입력을 축소한 뒤 다시 시도해주세요."
        )
    except FileNotFoundError:
        return (
            "❌ **codex 실행 파일을 찾을 수 없습니다**\n\n"
            "글로벌 설치가 누락되었습니다. `sudo npm install -g @openai/codex@latest`로 설치 후 다시 시도하세요."
        )

    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()

    if proc.returncode != 0:
        failure_text = f"{stdout}\n{stderr}".strip().lower()
        if any(marker in failure_text for marker in _LOGIN_MARKERS):
            return _LOGIN_REQUIRED_MESSAGE

        details = stderr or stdout or "원인을 알 수 없는 오류"
        return (
            "❌ **Codex 실행 실패**\n\n"
            f"{details}\n\n"
            "터미널에서 동일한 명령을 수동으로 실행해 상태를 확인해 주세요."
        )

    # Codex CLI may stream results on stdout or stderr depending on version
    content = stdout or stderr
    if not content:
        return (
            "⚠️ **Codex 응답 없음**\n\n"
            "Codex가 빈 응답을 반환했습니다. 입력을 다시 구성하거나 추가 컨텍스트를 제공해 보세요."
        )

    return content


def run_codex_high_with_fallback(
    query: str,
    context: str = "",
    persona: str = "high",
) -> Union[str, Dict[str, str]]:
    """High-effort reasoning wrapper that always calls the Codex CLI."""

    install_error = _ensure_codex_cli_latest()
    if install_error:
        return install_error

    prompt = _build_high_prompt(query, persona, context)
    return _run_codex_exec_high(prompt)


def run_codex(
    query: str,
    context: str = "",
    mode: str = "general",
    persona: str = "general",
    use_cli: bool = True,
) -> Union[str, Dict[str, str]]:
    """Unified Codex accessor with CLI-backed high reasoning."""

    if mode == "high":
        return run_codex_high_with_fallback(query, context, persona or "high")

    try:
        from .integration import call_codex_assistance

        return call_codex_assistance(query, context, persona or mode)
    except Exception as error:  # pragma: no cover - defensive fallback
        return {
            "error": f"Codex assistance failed: {error}",
            "hint": "Run 'codex exec' manually or check your Codex installation",
        }


def get_codex_status() -> Dict[str, Any]:
    """Report Codex installation status for diagnostics."""

    status: Dict[str, Any] = {
        "cli_available": shutil.which("codex") is not None,
        "npm_available": shutil.which("npm") is not None,
        "latest_version": None,
        "requires_login": False,
        "issues": [],
    }

    if not status["npm_available"]:
        status["issues"].append("npm not available (required for Codex CLI updates)")

    if not status["cli_available"]:
        status["issues"].append("codex CLI not found globally")

    # Check authentication status by probing codex auth info if available
    try:
        auth_check = subprocess.run(
            ["codex", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if auth_check.returncode != 0:
            combined = (auth_check.stdout + auth_check.stderr).lower()
            if any(marker in combined for marker in _LOGIN_MARKERS):
                status["requires_login"] = True
    except Exception:
        pass

    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")
    if api_key:
        status["api_key_present"] = True

    return status
