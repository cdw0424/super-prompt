# Super Prompt v5.0.0: Pure Python MCP Dual IDE Prompt Engineering Toolkit

## 🚀 **v5.0.0 Major Architecture Update**

**Complete transition to prompt-based workflow architecture!**

### ✨ **What's New in v5.0.0**
- **🔄 프롬프트 기반 워크플로우**: 모든 페르소나 함수가 프롬프트 기반으로 변환
- **🎯 모드별 특화**: GPT/Grok 모드별 최적화된 프롬프트 템플릿
- **🧹 코드 정리**: 불필요한 파이프라인 코드 제거 및 최적화
- **📈 성능 향상**: 간소화된 아키텍처로 더 빠른 응답 속도

[![PyPI version](https://img.shields.io/pypi/v/super-prompt-core.svg)](https://pypi.org/project/super-prompt-core/)
[![Python versions](https://img.shields.io/pypi/pyversions/super-prompt-core.svg)](https://pypi.org/project/super-prompt-core/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**🚀 The Ultimate Dual IDE Prompt Engineering Toolkit with Pure Python MCP
Implementation**

### ❗ Important: Enable Super‑Prompt MCP in Cursor

To use Super‑Prompt inside Cursor, ensure the Super‑Prompt MCP is enabled in
Cursor after initialization.

- Open Cursor → Settings → MCP and enable the Super‑Prompt server
- If you don’t see it, restart Cursor after running project initialization
- In chat, you should see slash command autocomplete like
  `/super-prompt/architect`

See the setup guide: [Cursor MCP Setup Guide](docs/cursor-mcp-setting-guide.md)

---

Super Prompt delivers advanced MCP (Model Context Protocol) implementation with
comprehensive development tools, seamless Cursor and Codex IDE integration, and
intelligent persona system.

### 🏗️ **New Architecture: Prompt-Based Workflow**

#### **🔄 프롬프트 기반 변환**
- **이전**: 복잡한 `_run_persona_pipeline` + `_PIPELINE_CONFIGS`
- **현재**: 간단한 `run_prompt_based_workflow` + 모드별 프롬프트 템플릿

#### **🎯 모드별 특화**
- **GPT 모드**: 구조화된 분석, 실용적 해결 방안
- **Grok 모드**: 최대한 진실된 분석, 현실적 고려사항

#### **📈 성능 최적화**
- 불필요한 파이프라인 로직 제거
- 프롬프트 템플릿 기반 빠른 응답
- 메모리 사용량 감소

### 🧭 Philosophy

- **Command First**: Explicit commands/flags take precedence and are executed
  immediately.
- **SSOT**: Single Source of Truth — personas manifest → `.cursor/rules` →
  `AGENTS.md`.
- **SDD**: Spec → Plan → Implement, with Acceptance Self‑Check before merge.
- **AMR**: Default to medium reasoning; switch to high for deep planning; return
  to medium for execution.
- **Safety**: English logs start with `-----`; never print secrets (mask like
  `sk-***`).

This philosophy powers a dual‑IDE workflow (Cursor + Codex) and underpins our
model recommendation below for consistent, fast, and reliable results.

### 🔍 Confession Mode (Double‑Check)

- **What it is**: An automatic self‑audit appended to the end of every MCP tool
  response.
- **What it includes**:
  - Summary of what was done
  - Unknowns and potential risks
  - Recommended countermeasures (verification/rollback/alternatives)
  - Completion timestamp
- **Scope**: Enabled by default for all Super Prompt MCP tool outputs in
  Cursor/Codex.
- **Purpose**: Standardizes a “double‑check” step to improve reliability and
  transparency of results.

### ✅ Recommended IDE Models (Cursor)

- Use both models together for best results:
  - GPT‑5 Codex (low, fast, max context)
  - Grok Code (fast, max context)

---

## ⚡ Quick Start

### 1) Install

```bash
# ⭐ 추천: Python 전용 설치 (Pure Python MCP 구현)
pip install super-prompt-core

# 설치 확인
super-prompt --help
super-prompt mcp --help
```

### 2) Initialize project assets

```bash
# 프로젝트 초기화 (모든 assets 자동 구성)
super-prompt super:init

# 또는 Python 모듈 직접 실행
python -m super_prompt super:init
```

### 3) MCP Client Usage

```bash
# MCP 서버 상태 확인
super-prompt mcp doctor

# 사용 가능한 도구 목록
super-prompt mcp list-tools

# 도구 호출 (대화형 모드)
super-prompt mcp call sp.list_commands --interactive

# 도구 호출 (JSON 인자)
super-prompt mcp call sp.architect --args-json '{"query": "design user auth system"}'
```

### 4) Enable in Cursor (MCP)

Open Cursor → Settings → MCP and enable the Super‑Prompt server (restart Cursor
if needed). After enabling, slash commands will autocomplete in chat.

MCP details (stdio)
- Transport: stdio (local child process). Cursor also supports HTTP/SSE, but stdio is recommended for local development. citeturn0search1
- Config locations: project `.cursor/mcp.json` (recommended) or global `~/.cursor/mcp.json`. Same schema in both. citeturn0search1turn0search2
- Minimal config:

```
{
  "mcpServers": {
    "super-prompt": {
      "type": "stdio",
      "command": "./bin/sp-mcp",
      "args": [],
      "env": {
        "SUPER_PROMPT_ALLOW_INIT": "true",
        "SUPER_PROMPT_REQUIRE_MCP": "1",
        "SUPER_PROMPT_PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONUNBUFFERED": "1",
        "PYTHONUTF8": "1"
      }
    }
  }
}
```

Programmatic registration: Cursor exposes an Extension API (`vscode.cursor.mcp.registerServer`) for dynamic registration from extensions, useful in enterprise setups. citeturn0search3

### 4.1) MCP Inspector로 로컬 stdio 서버 디버깅 (선택)

```
# 프로젝트 루트에서 실행
npx @modelcontextprotocol/inspector node ./bin/sp-mcp

# 브라우저에서 http://localhost:6274 접속 → Tools 호출 테스트
```

Inspector는 브라우저 기반 디버거로, stdio MCP 서버와의 상호작용을 시각적으로 점검할 수 있습니다. Node 22+ 필요. citeturn0search3

### 5) Model Modes (GPT vs Grok)

- Modes are mutually exclusive; default is GPT.
- In Cursor, toggle with slash commands (these persist the mode to
  `.super-prompt/mode.json` and switch the active provider):

```
 /super-prompt/gpt-mode-on
 /super-prompt/grok-mode-on
 /super-prompt/gpt-mode-off
 /super-prompt/grok-mode-off
```

- What happens:
  - `grok-mode-on`: sets mode to Grok (disables Codex AMR prompts), new chats
    use Grok.
  - `gpt-mode-on`: sets mode to GPT (enables Codex AMR prompts), new chats use
    GPT‑5 Codex.
  - `gpt-mode-off`/`grok-mode-off`: clear explicit mode; system will fall back
    to defaults.

- Codex CLI toggles (same behavior, affects both Cursor and Codex):

```bash
# Turn on GPT mode
sp gpt-mode-on

# Turn on Grok mode
sp grok-mode-on

# Turn off explicit GPT/Grok mode (revert to default)
sp gpt-mode-off
sp grok-mode-off
```

### 6) Codex Dependencies (for High Reasoning)

The `sp_high` tool uses **CLI-only execution** with automatic setup and authentication. It always starts with `sudo npm install` and handles login automatically.

#### Prerequisites
- **OpenAI CLI**: Install via `pip install openai`
- **Codex CLI**: Will be installed automatically via `sudo npm install -g @openai/codex@latest`
- **OpenAI Login**: Will be prompted automatically if not logged in
- **sudo access**: Required for npm global installation

#### How It Works
1. **Always Update CLI**: `sudo npm install -g @openai/codex@latest` (runs every time)
2. **Check Login Status**: `openai api keys.list`
3. **Auto Login**: If not logged in, launches `openai login` interactively
4. **Retry After Login**: If login succeeds, retries the entire process
5. **Execute Query**: Runs `openai codex high-plan` with your query

#### Execution Flow
```bash
# Every time you run /high:
sudo npm install -g @openai/codex@latest  # Always first
openai api keys.list                      # Check login
# If not logged in:
openai login                             # Interactive login
# Then retry from step 1
openai codex high-plan                   # Execute query
```

#### Troubleshooting sp_high Errors

If you encounter errors:

```bash
# Manual setup (if automatic fails)
pip install openai
sudo npm install -g @openai/codex@latest
openai login

# Check status
python -c "from super_prompt.codex.client import get_codex_status; import json; print(json.dumps(get_codex_status(), indent=2))"
```

Common error messages and solutions:
- **"sudo: command not found"**: Install sudo or run as root
- **"npm: command not found"**: Install Node.js and npm
- **"Codex login failed"**: Run `openai login` manually
- **"Permission denied"**: Ensure you have sudo access or run as root

**Note**: The tool always updates the CLI first and handles authentication automatically.

The enhanced error handling provides actionable hints to resolve dependency issues quickly.

### 7) Use in Cursor IDE

1. Set models as recommended above (GPT‑5 Codex low fast max + Grok Code fast
   max).
2. In Cursor chat, use slash commands:

```
 /super-prompt/architect "design a REST API"
/super-prompt/dev "implement authentication"
```

### 8) Use in Codex (flag commands)

In Codex, enter flags directly in chat (no `super-prompt` prefix). Recommended
flags use the `--sp-` prefix (both forms are accepted):

```
--sp-architect "design a REST API"
--sp-dev "implement authentication"
```

### 9) CLI usage

#### Python MCP 클라이언트 (권장)

```bash
# 도구 목록 조회
python -m super_prompt.mcp_client list-tools

# 도구 호출
python -m super_prompt.mcp_client call sp.architect --args-json '{"query": "design a REST API"}'

# 프롬프트 목록 조회
python -m super_prompt.mcp_client list-prompts

# 연결 상태 진단
python -m super_prompt.mcp_client doctor
```

#### Typer CLI (Python 패키지 설치 시)

```bash
super-prompt --version
super-prompt mcp-serve
super-prompt super:init
super-prompt doctor
super-prompt mcp list-tools
super-prompt mcp call sp.architect --args-json '{"query": "design a REST API"}'
```

#### NPM CLI (기존 방식 유지)

```bash
npx super-prompt --version
npx super-prompt mcp-serve
super-prompt --version  # 글로벌 설치 시
```

### 📦 Architecture (v4.7.0)

Super Prompt는 **Python 우선 아키텍처**로 전환하며 npm 생태계를 완전히 지원합니다:

```
super-prompt/
├── bin/
│   ├── super-prompt        # Bash CLI (npm 호환)
│   └── sp-mcp             # Python MCP 서버 launcher
├── packages/core-py/
│   ├── super_prompt/      # Python MCP 서버 (핵심 로직)
│   │   ├── mcp_client.py  # 🆕 Python MCP 클라이언트
│   │   └── cli.py         # Typer CLI with MCP commands
│   └── tests/             # 단위 테스트
├── packages/cursor-assets/  # IDE 통합 파일들
└── install.js             # Python 환경 자동 구성
```

**아키텍처 설계 원칙:**
- 🐍 **Python 우선**: 순수 Python MCP 클라이언트로 전환
- ⚡ **성능 최적화**: Python의 고성능 MCP SDK 활용
- 🔧 **자동 구성**: npm 설치 시 Python MCP 클라이언트 자동 구성
- 🚀 **점진적 마이그레이션**: Node.js 클라이언트에서 Python으로 전환 중

### Unified MCP pipeline

- Every `/super-prompt/<persona>` command now routes through a shared
  `sp.pipeline` helper.
- The pipeline always performs: memory lookup → prompt/context analysis →
  Codex/persona execution → plan + execution guidance → confession double-check
  → memory update.

---

## 🛠️ Available Tools

### Development

- `architect` - System architecture design
- `backend` - Backend development
- `frontend` - Frontend development
- `dev` - General development
- `refactorer` - Code refactoring
- `optimize` - Performance optimization

### Quality & Analysis

- `analyzer` - Code analysis
- `security` - Security review
- `performance` - Performance analysis
- `qa` - Quality assurance
- `review` - Code review

### Advanced

- `high` - Strategic analysis
- `doc-master` - Documentation
- `db-expert` - Database expertise

---

## 📚 Links

- **[Changelog](CHANGELOG.md)**: Version history
- **[Issues](https://github.com/cdw0424/super-prompt/issues)**: Report bugs

## 📄 License

MIT © [Daniel Choi](https://github.com/cdw0424)
