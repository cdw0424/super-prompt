# packages/core-py/super_prompt/codex/client.py
"""
Codex client with API-first and CLI fallback.
Prioritizes API for speed, falls back to CLI with auto-login.
"""

import os
import sys
import json
import shlex
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CodexUnavailableError(Exception):
    """Raised when Codex dependencies are missing or unavailable."""
    error_type: str
    message: str
    hint: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "error": f"{self.error_type}: {self.message}",
            "hint": self.hint
        }


def _check_codex_dependencies() -> Optional[CodexUnavailableError]:
    """
    Check if Codex dependencies are available and properly configured.
    Returns CodexUnavailableError if any dependency is missing, None if all good.
    """

    # Check for Codex MCP bridge
    try:
        from ..paths import package_root
        bridge_path = package_root() / "src" / "tools" / "codex-mcp.js"
        if not bridge_path.exists():
            return CodexUnavailableError(
                error_type="MissingMCPBridge",
                message="Codex MCP bridge file is missing",
                hint=f"Ensure codex-mcp.js exists at {bridge_path}"
            )
    except Exception as e:
        return CodexUnavailableError(
            error_type="MCPBridgeError",
            message=f"Cannot locate MCP bridge: {e}",
            hint="Check Super Prompt installation and file structure"
        )

    return None  # Dependencies are available


def _run_codex_high_cli(query: str, context: str = "", retry_after_login: bool = False) -> str:
    """
    CLI execution for high reasoning with proactive installation and login.
    Automatically handles CLI installation, update, and login when missing.
    """
    import subprocess
    import shutil

    # Step 1: Check if OpenAI CLI is available, install if missing
    if not retry_after_login:  # Only check/install on first attempt
        openai_path = shutil.which("openai")
        if not openai_path:

            # First, try to install OpenAI CLI via pip
            try:
                pip_proc = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "openai"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=120
                )
                if pip_proc.returncode != 0:
                    return """❌ **OpenAI CLI 설치 실패**

OpenAI CLI를 설치할 수 없습니다.

## 🔧 해결 방법:

### 1. 수동 설치
```bash
pip install openai
```

### 2. 권한 문제인 경우
```bash
pip install --user openai
```

### 3. Python 버전 확인
```bash
python --version  # Python 3.8+ 권장
pip --version
```

설치 완료 후 다시 시도해주세요."""

            except subprocess.TimeoutExpired:
                return "❌ **설치 시간 초과**\n\nOpenAI CLI 설치가 너무 오래 걸립니다. 수동으로 설치해주세요."
            except Exception as e:
                return f"❌ **설치 오류**: {str(e)}\n\n수동으로 설치해주세요."

        # Step 2: Install/Update Codex CLI
        try:
            update_proc = subprocess.run(
                ["sudo", "npm", "install", "-g", "@openai/codex@latest"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=180
            )
            if update_proc.returncode != 0:
                # Check if npm is available
                npm_path = shutil.which("npm")
                if not npm_path:
                    return """❌ **npm이 설치되어 있지 않습니다**

Codex CLI를 설치하려면 Node.js와 npm이 필요합니다.

## 🔧 Node.js 설치 방법:

### macOS (권장):
```bash
# Homebrew 사용
brew install node

# 또는 공식 설치 프로그램
# https://nodejs.org/ 에서 다운로드
```

### 다른 OS:
- **Windows**: https://nodejs.org/ 에서 설치
- **Linux**: 패키지 매니저 사용 (`apt install nodejs npm`)

설치 완료 후 다시 시도해주세요."""
            else:
        except subprocess.TimeoutExpired:
        except Exception as e:

    # Step 3: Check login status and login if needed
    try:
        check = subprocess.run(
            ["openai", "api", "keys", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )

        # Step 4: If not logged in, launch login
        if check.returncode != 0:

            try:
                login_proc = subprocess.run(
                    ["openai", "login"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=300  # 5 minutes for login
                )

                if login_proc.returncode != 0:
                    error_msg = login_proc.stderr.strip() or login_proc.stdout.strip() or "Login failed"
                    return f"""❌ **OpenAI 로그인 실패**

로그인 과정에서 오류가 발생했습니다.

## 🔧 해결 방법:

### 1. 수동 로그인
```bash
openai login
```

### 2. 브라우저에서 로그인
명령어 실행 시 브라우저가 열리면 인증을 완료해주세요.

### 3. API 키 직접 설정 (선택사항)
환경변수에 OpenAI API 키를 설정할 수도 있습니다:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 오류 상세:
{error_msg}

로그인 완료 후 다시 시도해주세요."""

                # Retry after successful login
                return _run_codex_high_cli(query, context, retry_after_login=True)

            except subprocess.TimeoutExpired:
                return """❌ **로그인 시간 초과**

OpenAI 로그인 과정이 너무 오래 걸립니다.

## 🔧 해결 방법:

1. **수동 로그인**:
   ```bash
   openai login
   ```

2. **브라우저에서 완료**:
   - 로그인 명령어 실행 시 열리는 브라우저에서 인증을 완료해주세요
   - 인증이 완료될 때까지 기다려주세요

다시 시도해주세요."""

    except FileNotFoundError:
        return """❌ **OpenAI CLI를 찾을 수 없습니다**

OpenAI CLI가 제대로 설치되지 않았습니다.

## 🔧 재설치 방법:
```bash
# 기존 설치 제거 (선택사항)
pip uninstall openai

# 재설치
pip install openai

# Codex CLI 재설치
sudo npm install -g @openai/codex@latest
```

설치 완료 후 다시 시도해주세요."""

    # Step 5: Execute Codex high plan
    try:
        payload = json.dumps({"query": query, "context": context or ""})
        proc = subprocess.run(
            ["openai", "codex", "high-plan"],
            input=payload,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=300  # 5 minutes for execution
        )

        if proc.returncode != 0:
            error_msg = proc.stderr.strip() or proc.stdout.strip() or "Unknown error"
            return f"""❌ **Codex CLI 실행 실패**

고수준 추론을 실행하는 중 오류가 발생했습니다.

## 🔧 해결 방법:

1. **재시도**: 동일한 쿼리로 다시 시도해보세요
2. **CLI 상태 확인**:
   ```bash
   openai --version
   openai api keys.list
   ```

3. **업데이트**:
   ```bash
   sudo npm update -g @openai/codex@latest
   ```

### 오류 상세:
{error_msg}

문제가 지속되면 OpenAI CLI나 Codex CLI의 최신 버전을 확인해주세요."""

        result = proc.stdout.strip()
        if not result:
            return """⚠️ **출력 없음**

Codex CLI가 응답을 생성했지만 내용이 비어있습니다.

## 🔧 해결 방법:

1. **쿼리 재구성**: 더 구체적인 질문을 시도해보세요
2. **컨텍스트 추가**: 추가 정보를 제공해보세요
3. **재시도**: 동일한 쿼리로 다시 시도해보세요

예시:
- "빅뱅 이론에 대해 자세히 설명해주세요"
- "우주의 기원과 진화 과정에 대해 알려주세요" """

        return result

    except subprocess.TimeoutExpired:
        return """❌ **실행 시간 초과**

Codex CLI 실행이 5분을 초과했습니다.

## 🔧 해결 방법:

1. **더 간단한 쿼리**: 복잡한 질문을 간단하게 나누어 시도해보세요
2. **네트워크 확인**: 인터넷 연결 상태를 확인해주세요
3. **재시도**: 동일한 쿼리로 다시 시도해보세요

시간이 오래 걸리는 경우 OpenAI 서비스 상태를 확인해주세요."""

    except Exception as e:
        return f"""❌ **예상치 못한 오류**

시스템 오류가 발생했습니다.

## 🔧 해결 방법:

1. **재시도**: 동일한 쿼리로 다시 시도해보세요
2. **CLI 재설치**:
   ```bash
   pip install --upgrade openai
   sudo npm install -g @openai/codex@latest
   ```

3. **로그 확인**: 터미널에서 자세한 오류 로그를 확인해주세요

### 오류 상세:
{str(e)}

문제가 지속되면 시스템 관리자에게 문의해주세요."""


def run_codex_high_with_fallback(query: str, context: str = "") -> Union[str, Dict[str, str]]:
    """
    High reasoning that always uses CLI with automatic update and login.
    Follows the flow: npm install -> check login -> execute, with retry after login.
    """
    try:
        return _run_codex_high_cli(query, context)
    except Exception as cli_error:
        return {
            "error": f"Codex CLI execution failed: {str(cli_error)}",
            "hint": "Try running 'sudo npm install -g @openai/codex@latest' and 'openai login' manually"
        }


def run_codex(
    query: str,
    context: str = "",
    mode: str = "general",
    use_cli: bool = True
) -> Union[str, Dict[str, str]]:
    """
    Unified Codex assistance with API-first, CLI fallback.
    """
    if mode == "high":
        return run_codex_high_with_fallback(query, context)

    # For other modes, try the existing integration
    try:
        from .integration import call_codex_assistance
        return call_codex_assistance(query, context, mode)
    except Exception as e:
        return {
            "error": f"Codex assistance failed: {str(e)}",
            "hint": "Check your OpenAI API key or try 'openai login'"
        }


def get_codex_status() -> Dict[str, Any]:
    """
    Get comprehensive status of Codex configuration with API and CLI info.
    """
    import subprocess

    status = {
        "method": "api-first-with-cli-fallback",
        "api_available": False,
        "cli_available": False,
        "npm_available": False,
        "available": False,
        "issues": []
    }

    # Check npm availability (for CLI updates)
    try:
        npm_result = subprocess.run(["npm", "--version"], capture_output=True, timeout=3)
        status["npm_available"] = npm_result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        status["issues"].append("npm not available (needed for CLI updates)")

    # Check OpenAI CLI installation
    try:
        openai_result = subprocess.run(["openai", "--version"], capture_output=True, timeout=3)
        status["cli_available"] = openai_result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        status["issues"].append("OpenAI CLI not found or not working")

    # Check API key
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")
    status["api_available"] = bool(api_key)

    # Overall availability - either API or CLI should work
    status["available"] = status["api_available"] or status["cli_available"]

    return status
