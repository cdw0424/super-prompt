#!/usr/bin/env python3
# Cursor Tag Executor — Python port
# - Dispatches persona tags (e.g., "/frontend") to super-prompt optimize
# - Provides SDD helpers: `sdd spec|plan|tasks|implement <text>`
# - Provides debate mode: append `/debate` (requires `codex` CLI)

import os
import re
import sys
import shlex
import shutil
import subprocess
import datetime

# Ensure PATH includes common CLI locations (helps Cursor GUI env)
_DEFAULT_PATHS = [
    "/opt/homebrew/bin",
    "/usr/local/bin",
    "/usr/bin",
    "/bin",
]
os.environ["PATH"] = ":".join(_DEFAULT_PATHS + [os.environ.get("PATH", "")])

def upgrade_codex_latest():
    if os.environ.get('SP_SKIP_CODEX_UPGRADE') == '1':
        return
    npm = shutil.which('npm')
    if not npm:
        return
    try:
        _ = subprocess.run([npm, 'install', '-g', '@openai/codex@latest'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def upgrade_self_latest():
    if os.environ.get('SP_SKIP_SELF_UPDATE') == '1':
        return
    npm = shutil.which('npm')
    if not npm:
        return
    try:
        _ = subprocess.run([npm, 'install', '-g', '@cdw0424/super-prompt@latest'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def log(msg: str):
    print(f"-------- {msg}")


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    if os.environ.get('SP_DEBUG'):
        print(f"DEBUG exec: {' '.join(shlex.quote(c) for c in cmd)}")
    p = subprocess.run(cmd, text=True)
    if os.environ.get('SP_DEBUG'):
        print(f"DEBUG returncode: {p.returncode}")
    return p


def _call_capture(cmd: list[str], timeout: int = 120) -> str:
    try:
        if os.environ.get('SP_DEBUG'):
            print(f"DEBUG exec(cap): {' '.join(shlex.quote(c) for c in cmd)}")
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (p.stdout or "").strip()
    except Exception as e:
        log(f"execution failed: {e}")
        return ""


def run_optimize(text: str) -> int:
    if shutil.which("super-prompt"):
        return _run(["super-prompt", "optimize", text]).returncode
    return _run(["npx", "@cdw0424/super-prompt", "optimize", text]).returncode


def is_debate(text: str) -> bool:
    return "/debate" in text or " --debate" in text

def is_debate_interactive(text: str) -> bool:
    return "/debate-interactive" in text or "--debate-interactive" in text or " --interactive" in text

def has_strict_flag(text: str) -> bool:
    return "--strict" in text or os.environ.get('SP_STRICT_EXTERNAL') == '1'


def parse_debate_opts(text: str) -> tuple[str, int]:
    """Extract debate options like --rounds/--round N and return (topic, rounds)."""
    rounds = 10
    # --rounds N | --rounds=N | --round N | --round=N
    m = re.search(r"--rounds\s*=\s*(\d+)|--rounds\s+(\d+)|--round\s*=\s*(\d+)|--round\s+(\d+)", text)
    if m:
        rounds = int(next(g for g in m.groups() if g))
    s = re.sub(r"\s*/debate\b", "", text)
    s = re.sub(r"\s*--debate\b", "", s)
    s = re.sub(r"\s*--rounds?(\s*=\s*\d+|\s+\d+)", "", s)
    s = re.sub(r"\s*--strict\b", "", s)
    return s.strip(), max(2, min(rounds, 50))

def parse_debate_interactive_opts(text: str) -> tuple[str, int]:
    rounds = 10
    m = re.search(r"--rounds\s*=\s*(\d+)|--rounds\s+(\d+)|--round\s*=\s*(\d+)|--round\s+(\d+)", text)
    if m:
        rounds = int(next(g for g in m.groups() if g))
    s = re.sub(r"\s*/debate-interactive\b", "", text)
    s = re.sub(r"\s*--debate-interactive\b", "", s)
    s = re.sub(r"\s*/debate\b", "", s)
    s = re.sub(r"\s*--interactive\b", "", s)
    s = re.sub(r"\s*--rounds?(\s*=\s*\d+|\s+\d+)", "", s)
    s = re.sub(r"\s*--strict\b", "", s)
    return s.strip(), max(2, min(rounds, 50))


def run_debate(topic: str, rounds: int = 10, strict: bool = False) -> int:
    if not shutil.which("codex"):
        msg = "❌ Debate mode requires 'codex' CLI on PATH."
        print(msg)
        return 2 if strict else 1

    # Prefer alternating models if available: CRITIC=codex, CREATOR=claude (fallback codex)
    have_claude = bool(shutil.which("claude"))
    have_openai = bool(shutil.which("openai"))
    creator_cmd_tpl = os.environ.get('SP_CREATOR_CMD','').strip()

    def call_codex(prompt: str) -> str:
        if os.environ.get('SP_VERBOSE'):
            print("-------- ENGINE: codex (high)")
            print("-------- PROMPT BEGIN\n" + prompt + "\n-------- PROMPT END")
        out = _call_capture(["codex", "exec", "-c", "model_reasoning_effort=high", prompt])
        if strict and not out:
            print("❌ Strict mode: codex returned no output.")
            sys.exit(2)
        return out

    def call_claude(prompt: str) -> str:
        if not have_claude:
            return call_codex(prompt)
        if os.environ.get('SP_VERBOSE'):
            print("-------- ENGINE: claude (sonnet)")
            print("-------- PROMPT BEGIN\n" + prompt + "\n-------- PROMPT END")
        out = _call_capture(["claude", "--model", "claude-sonnet-4-20250514", "-p", prompt], timeout=90)
        if strict and not out:
            print("❌ Strict mode: claude returned no output.")
            sys.exit(2)
        return out

    def call_openai(prompt: str) -> str:
        model = os.environ.get('SP_OPENAI_MODEL', 'gpt-4o')
        if os.environ.get('SP_VERBOSE'):
            print(f"-------- ENGINE: openai ({model})")
            print("-------- PROMPT BEGIN\n" + prompt + "\n-------- PROMPT END")
        out = _call_capture(["openai","chat.completions.create","-m", model, "-g", "system", "You are a helpful assistant.", "-g", "user", prompt], timeout=120)
        if out:
            return out
        out = _call_capture(["openai","api","chat.completions.create","-m", model, "-g", "system", "You are a helpful assistant.", "-g", "user", prompt], timeout=120)
        if strict and not out:
            print("❌ Strict mode: openai returned no output.")
            sys.exit(2)
        return out

    def call_custom(prompt: str) -> str:
        cmd_tpl = creator_cmd_tpl
        if os.environ.get('SP_VERBOSE'):
            print("-------- ENGINE: custom (SP_CREATOR_CMD)")
            print("-------- PROMPT BEGIN\n" + prompt + "\n-------- PROMPT END")
        if '{prompt}' in cmd_tpl:
            cmd = cmd_tpl.replace('{prompt}', prompt)
            out = _call_capture(shlex.split(cmd), timeout=180)
            if strict and not out:
                print("❌ Strict mode: custom CREATOR returned no output.")
                sys.exit(2)
            return out
        parts = shlex.split(cmd_tpl)
        try:
            p = subprocess.run(parts, input=prompt, capture_output=True, text=True, timeout=180)
            return (p.stdout or "").strip()
        except Exception as e:
            log(f"custom engine failed: {e}")
            if strict:
                print("❌ Strict mode: custom CREATOR failed.")
                sys.exit(2)
            return ""

    def only_role(role: str, text: str) -> str:
        # Keep only the current role's content; strip other role headers, code fences, etc.
        t = text.strip()
        t = re.sub(r"^```[a-zA-Z]*|```$", "", t, flags=re.M)
        # If the model included both roles, cut at the first occurrence of the other role marker
        other = "CREATOR" if role == "CRITIC" else "CRITIC"
        idx = re.search(rf"^\s*{other}\s*:|^\s*{other}\b", t, flags=re.I | re.M)
        if idx:
            t = t[: idx.start()].rstrip()
        # Remove leading role labels for cleanliness
        t = re.sub(rf"^\s*{role}\s*:\s*", "", t, flags=re.I)
        # Enforce max 10 lines and prefix
        lines = [ln for ln in t.strip().splitlines() if ln.strip()]
        lines = lines[:10]
        body = "\n".join(lines).strip()
        return f"{role}: {body}" if not body.startswith(f"{role}:") else body

    def build_prompt(role: str, other_text: str, i: int, n: int, initial: bool = False) -> str:
        shared_rules = (
            "HARD CONSTRAINTS (read carefully):\n"
            "- Output ONLY the {role} message for THIS TURN.\n"
            "- NEVER include both roles in one answer.\n"
            "- DO NOT summarize the debate or provide final conclusions early.\n"
            "- DO NOT simulate the other role.\n"
            "- LIMIT to 10 non-empty lines, no code fences, no headings.\n"
            "- Begin the first line with '{role}: ' then the content.\n"
        )
        if role == "CRITIC":
            sys_rules = (
                "You are CODEX-CRITIC: a rigorous, logic-first debater.\n"
                + shared_rules.format(role="CRITIC") +
                "TASK: Point out flaws, missing assumptions, risks; propose 1-2 concrete, testable validations.\n"
            )
            ctx = f"Round {i}/{n} — Topic: {topic}\nCREATOR said: {other_text or '(first turn)'}"
        else:
            sys_rules = (
                "You are CURSOR-CREATOR: a positive, creative collaborator.\n"
                + shared_rules.format(role="CREATOR") +
                "TASK: Build constructively on CRITIC, propose improved approach and small actionable steps.\n"
            )
            if initial:
                ctx = f"Round {i}/{n} — Topic: {topic}\nFRAMING: Provide an initial, concrete stance and 2-3 small steps."
            else:
                ctx = f"Round {i}/{n} — Topic: {topic}\nCRITIC said: {other_text}"
        return f"{sys_rules}\n\nCONTEXT:\n{ctx}"

    print("-------- Debate start (/debate): CURSOR-CREATOR ↔ CODEX-CRITIC")
    transcript: list[str] = []
    creator_last = ""
    critic_last = ""
    # Decide creator engine once per session (single chat)
    creator_engine = 'custom' if creator_cmd_tpl else ('claude' if have_claude else ('openai' if have_openai else 'codex'))

    for i in range(1, rounds + 1):
        # CREATOR starts each round (initial framing on first round)
        k_prompt = build_prompt("CREATOR", critic_last, i, rounds, initial=(i == 1))
        if creator_engine == 'custom':
            print(f">> [CREATOR] engine=custom round {i}/{rounds}")
            k_out_raw = call_custom(k_prompt) or "(no output)"
        elif creator_engine == 'openai':
            print(f">> [CREATOR] engine=openai round {i}/{rounds}")
            k_out_raw = call_openai(k_prompt) or "(no output)"
        elif creator_engine == 'claude':
            print(f">> [CREATOR] engine=claude round {i}/{rounds}")
            k_out_raw = call_claude(k_prompt) or "(no output)"
        else:
            print(f">> [CREATOR] engine=codex/high round {i}/{rounds}")
            k_out_raw = call_codex(k_prompt) or "(no output)"
        k_out = only_role("CREATOR", k_out_raw)
        if strict and not k_out_raw:
            print("❌ Strict mode: CREATOR produced no output.")
            return 2
        print(f"\n[Turn {i} — CURSOR-CREATOR]\n{k_out}\n")
        transcript.append(f"[Turn {i} — CURSOR-CREATOR]\n{k_out}\n")
        creator_last = k_out

        # CRITIC responds
        c_prompt = build_prompt("CRITIC", creator_last, i, rounds)
        print(f">> [CRITIC] engine=codex/high round {i}/{rounds}")
        c_out_raw = call_codex(c_prompt) or "(no output)"
        c_out = only_role("CRITIC", c_out_raw)
        if strict and not c_out_raw:
            print("❌ Strict mode: codex produced no output.")
            return 2
        print(f"[Turn {i} — CODEX-CRITIC]\n{c_out}\n")
        transcript.append(f"[Turn {i} — CODEX-CRITIC]\n{c_out}\n")
        critic_last = c_out

    # Final synthesis via codex (or claude if available)
    fin = (
        "Synthesize the best combined outcome from the debate transcript. "
        "Provide a concise final recommendation with a 5-step plan and checks.\n\n"
        + "\n".join(transcript[-6:])
    )
    final_out = call_claude(fin) if have_claude else call_codex(fin)
    final_out = final_out or "(no output)"
    if strict and not final_out:
        print("❌ Strict mode: Final synthesis produced no output.")
        return 2
    print("[Final Synthesis]\n" + final_out + "\n")

    # Optionally save transcript
    if os.environ.get('SP_SAVE_DEBATE', '1') == '1':
        def slug(s: str) -> str:
            s = re.sub(r"[^a-zA-Z0-9가-힣]+", "-", s.strip())
            s = re.sub(r"-+", "-", s).strip('-')
            return s or "debate"
        ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        name = f"{slug(topic)[:40]}_R{rounds}_{ts}.md"
        out_dir = os.path.join('debates')
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# Debate — {topic}\n\n")
            f.write(f"Rounds: {rounds}\nGenerated: {ts}\n\n")
            f.write("## Transcript\n\n" + "\n".join(transcript) + "\n\n")
            f.write("## Final Synthesis\n\n" + final_out + "\n")
        print(f"-------- Debate transcript saved → {path}")
    return 0


def run_debate_interactive(topic: str, total_rounds: int = 10, strict: bool = False) -> int:
    # State file per topic slug
    def slug(s: str) -> str:
        s = re.sub(r"[^a-zA-Z0-9가-힣]+", "-", s.strip())
        s = re.sub(r"-+", "-", s).strip('-')
        return s or "debate"
    topic_slug = slug(topic)
    state_dir = os.path.join('debates', 'state')
    os.makedirs(state_dir, exist_ok=True)
    state_path = os.path.join(state_dir, f"{topic_slug}.json")

    # Load state
    state = {
        "topic": topic,
        "total_rounds": total_rounds,
        "current_round": 0,
        "creator_engine": None,
        "transcript": [],
        "completed": False,
    }
    if os.path.exists(state_path):
        try:
            import json
            with open(state_path, 'r', encoding='utf-8') as f:
                prev = json.load(f)
                if prev.get('topic'): state['topic'] = prev['topic']
                if prev.get('total_rounds'): state['total_rounds'] = prev['total_rounds']
                if prev.get('current_round') is not None: state['current_round'] = prev['current_round']
                if prev.get('creator_engine'): state['creator_engine'] = prev['creator_engine']
                if prev.get('transcript'): state['transcript'] = prev['transcript']
                if prev.get('completed') is not None: state['completed'] = prev['completed']
        except Exception as e:
            log(f"state load failed: {e}")

    if state['completed']:
        print(f"✅ Debate already completed for topic: {topic}")
        print(f"   State: {state_path}")
        return 0

    # Engine selection consistent for session
    have_claude = bool(shutil.which("claude"))
    have_openai = bool(shutil.which("openai"))
    creator_cmd_tpl = os.environ.get('SP_CREATOR_CMD','').strip()
    if not state['creator_engine']:
        if creator_cmd_tpl:
            state['creator_engine'] = 'custom'
        elif have_claude:
            state['creator_engine'] = 'claude'
        elif have_openai:
            state['creator_engine'] = 'openai'
        else:
            state['creator_engine'] = 'codex'

    # Helpers reused from batch debate
    def call_codex(prompt: str) -> str:
        if os.environ.get('SP_VERBOSE'):
            print("-------- ENGINE: codex (high)")
            print("-------- PROMPT BEGIN\n" + prompt + "\n-------- PROMPT END")
        return _call_capture(["codex", "exec", "-c", "model_reasoning_effort=high", prompt])
    def call_claude(prompt: str) -> str:
        if not have_claude:
            return call_codex(prompt)
        if os.environ.get('SP_VERBOSE'):
            print("-------- ENGINE: claude (sonnet)")
            print("-------- PROMPT BEGIN\n" + prompt + "\n-------- PROMPT END")
        return _call_capture(["claude", "--model", "claude-sonnet-4-20250514", "-p", prompt], timeout=90)
    def call_openai(prompt: str) -> str:
        model = os.environ.get('SP_OPENAI_MODEL', 'gpt-4o')
        if os.environ.get('SP_VERBOSE'):
            print(f"-------- ENGINE: openai ({model})")
            print("-------- PROMPT BEGIN\n" + prompt + "\n-------- PROMPT END")
        out = _call_capture(["openai","chat.completions.create","-m", model, "-g", "system", "You are a helpful assistant.", "-g", "user", prompt], timeout=120)
        if out:
            return out
        return _call_capture(["openai","api","chat.completions.create","-m", model, "-g", "system", "You are a helpful assistant.", "-g", "user", prompt], timeout=120)
    def call_custom(prompt: str) -> str:
        cmd_tpl = creator_cmd_tpl
        if os.environ.get('SP_VERBOSE'):
            print("-------- ENGINE: custom (SP_CREATOR_CMD)")
            print("-------- PROMPT BEGIN\n" + prompt + "\n-------- PROMPT END")
        if '{prompt}' in cmd_tpl:
            cmd = cmd_tpl.replace('{prompt}', prompt)
            return _call_capture(shlex.split(cmd), timeout=180)
        parts = shlex.split(cmd_tpl)
        try:
            p = subprocess.run(parts, input=prompt, capture_output=True, text=True, timeout=180)
            return (p.stdout or "").strip()
        except Exception as e:
            log(f"custom engine failed: {e}")
            return ""
    def only_role(role: str, text: str) -> str:
        t = text.strip()
        t = re.sub(r"^```[a-zA-Z]*|```$", "", t, flags=re.M)
        other = "CREATOR" if role == "CRITIC" else "CRITIC"
        idx = re.search(rf"^\s*{other}\s*:|^\s*{other}\b", t, flags=re.I | re.M)
        if idx: t = t[: idx.start()].rstrip()
        t = re.sub(rf"^\s*{role}\s*:\s*", "", t, flags=re.I)
        lines = [ln for ln in t.strip().splitlines() if ln.strip()][:10]
        body = "\n".join(lines).strip()
        return f"{role}: {body}" if not body.startswith(f"{role}:") else body
    def build_prompt(role: str, other_text: str, i: int, n: int, initial: bool = False) -> str:
        shared_rules = (
            "HARD CONSTRAINTS (read carefully):\n"
            "- Output ONLY the {role} message for THIS TURN.\n"
            "- NEVER include both roles in one answer.\n"
            "- DO NOT summarize early.\n"
            "- LIMIT to 10 lines; begin with '{role}: '.\n"
        )
        if role == "CREATOR":
            sys_rules = (
                "You are CURSOR-CREATOR: positive, creative collaborator.\n"
                + shared_rules.format(role="CREATOR") +
                "TASK: build on CRITIC; propose improved approach + small actionable steps.\n"
            )
            ctx = f"Round {i}/{n} — Topic: {topic}\n" + ("FRAMING: Provide initial stance + 2-3 steps." if initial else f"CRITIC said: {other_text}")
        else:
            sys_rules = (
                "You are CODEX-CRITIC: rigorous, logic-first debater.\n"
                + shared_rules.format(role="CRITIC") +
                "TASK: point out flaws/assumptions/risks; 1-2 testable validations.\n"
            )
            ctx = f"Round {i}/{n} — Topic: {topic}\nCREATOR said: {other_text or '(first turn)'}"
        return f"{sys_rules}\n\nCONTEXT:\n{ctx}"

    i = state['current_round'] + 1
    n = state['total_rounds']
    if i > n:
        print("✅ Debate already completed. Re-run with a new topic or remove state file to restart.")
        print(f"   State: {state_path}")
        return 0

    print(f"-------- Debate interactive — round {i}/{n}")
    # CREATOR turn
    k_prompt = build_prompt("CREATOR", "" if i == 1 else state['transcript'][-1], i, n, initial=(i == 1))
    if state['creator_engine'] == 'custom':
        k_out_raw = call_custom(k_prompt) or "(no output)"
    elif state['creator_engine'] == 'openai':
        k_out_raw = call_openai(k_prompt) or "(no output)"
    elif state['creator_engine'] == 'claude':
        k_out_raw = call_claude(k_prompt) or "(no output)"
    else:
        k_out_raw = call_codex(k_prompt) or "(no output)"
    k_out = only_role("CREATOR", k_out_raw)
    if strict and not k_out_raw:
        print("❌ Strict mode: CREATOR produced no output.")
        return 2
    print(f"[CREATOR]\n{k_out}\n")
    state['transcript'].append(k_out)

    # CRITIC turn
    c_prompt = build_prompt("CRITIC", k_out, i, n)
    c_out_raw = call_codex(c_prompt) or "(no output)"
    c_out = only_role("CRITIC", c_out_raw)
    if strict and not c_out_raw:
        print("❌ Strict mode: codex produced no output.")
        return 2
    print(f"[CRITIC]\n{c_out}\n")
    state['transcript'].append(c_out)

    state['current_round'] = i
    # Completion check
    done = i >= n
    if done:
        fin = (
            "Synthesize the best combined outcome from the debate transcript. "
            "Provide a concise final recommendation with a 5-step plan and checks.\n\n"
            + "\n".join(state['transcript'][-6:])
        )
        final_out = call_codex(fin)
        print("[Final Synthesis]\n" + (final_out or "(no output)") + "\n")
        if strict and not final_out:
            print("❌ Strict mode: Final synthesis produced no output.")
            return 2
        state['completed'] = True

    # Save state
    try:
        import json
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print(f"-------- Saved state → {state_path}")
    except Exception as e:
        log(f"state save failed: {e}")

    if not done:
        print("➡️  Re-run the same command to continue to the next round.")
    else:
        print("✅ Debate completed. Start a new topic or remove the state file to restart.")
    return 0


SDD_RE = re.compile(r"^sdd\s+(spec|plan|tasks|implement)\s*(.*)$", re.I)


def run_sdd(text: str) -> int:
    m = SDD_RE.match(text.strip())
    if not m:
        return 2
    sub = m.group(1).lower()
    user_input = m.group(2).strip()

    if sub == "spec":
        header = (
            "[SDD SPEC REQUEST]\n"
            "요구사항을 바탕으로 다음 템플릿으로 SPEC 문서를 작성하세요.\n\n"
            "- 문제정의/배경\n- 목표와 사용자 가치\n- 성공 기준(정량/정성)\n- 범위 / 비범위\n- 제약/가정\n- 이해관계자/의존성\n"
            "- 상위 수준 아키텍처(간단 스케치)\n- 수용 기준 초안\n\n[주의]\n"
            "- 스택/벤더 선택 강제 금지(필요 시 옵션 비교만)\n- 간결/구조화, 불필요한 구현 세부 금지"
        )
        composed = f"{header}\n\n[사용자 요청]\n{user_input} /architect"
        return run_optimize(composed)

    if sub == "plan":
        header = (
            "[SDD PLAN REQUEST]\n다음 템플릿으로 구현 계획을 작성하세요.\n\n"
            "- 아키텍처 구성요소와 책임\n- 데이터/계약(API·이벤트) 개요\n- 단계별 구현 계획(작은 스텝)\n- 리스크/대안/롤백 포인트\n"
            "- 비기능 고려사항(성능/보안/관측성 등)\n- 수용 기준 체크리스트\n\n[주의]\n"
            "- 큰 변경 대신 작은 단계로 분해\n- 테스트 가능성과 추적성 강조"
        )
        composed = f"{header}\n\n[사용자 요청]\n{user_input} /architect"
        return run_optimize(composed)

    if sub == "tasks":
        header = (
            "[SDD TASKS REQUEST]\nPLAN을 기반으로 다음 형식으로 작업을 분해하세요.\n\n"
            "- [TASK-ID] 제목\n  - 설명\n  - 산출물(파일/결과)\n  - 수용 기준\n  - 예상치/우선순위/의존성\n\n[주의]\n"
            "- 코드 변경은 최소 단위로 나누고 독립적으로 검증 가능하게"
        )
        composed = f"{header}\n\n[사용자 요청]\n{user_input} /analyzer"
        return run_optimize(composed)

    if sub == "implement":
        header = (
            "[SDD IMPLEMENT REQUEST]\nSPEC/PLAN을 준수하는 최소 구현 접근을 제안하세요.\n\n"
            "- 변경 파일/디렉터리 개요(추가/수정/삭제 금지 여부)\n- 단계별 적용 순서(작은 커밋 지향)\n"
            "- 리스크와 대응(되돌리기 포인트 포함)\n- 검증 방법(테스트/검수)\n\n[주의]\n"
            "- 범위 밖 변경 금지, 기존 패턴 우선 준수"
        )
        composed = f"{header}\n\n[사용자 요청]\n{user_input} /architect"
        return run_optimize(composed)

    return 2


def main(argv: list[str]) -> int:
    # Always try to ensure codex is latest (can be skipped via SP_SKIP_CODEX_UPGRADE=1)
    upgrade_self_latest()
    upgrade_codex_latest()
    if len(argv) <= 1:
        print("❌ Usage: tag-executor.py \"your question /tag\"")
        print("\n📋 Available Tags:")
        print("  /frontend-ultra, /frontend, /backend, /analyzer, /architect, /high, /seq, /seq-ultra, /debate")
        print("  SDD: sdd spec|plan|tasks|implement <text>")
        return 1

    text = " ".join(argv[1:]).strip()

    # Debate mode
    if is_debate(text):
        topic, rounds = parse_debate_opts(text)
        strict = has_strict_flag(text)
        # Interactive flag also triggers interactive debate
        if is_debate_interactive(text):
            return run_debate_interactive(topic, total_rounds=rounds, strict=strict)
        return run_debate(topic, rounds=rounds, strict=strict)

    # SDD helpers
    if text.lower().startswith("sdd "):
        rc = run_sdd(text)
        if rc in (0, 1):
            return rc

    # Fallback: forward to optimize path (persona tags included in text)
    return run_optimize(text)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
