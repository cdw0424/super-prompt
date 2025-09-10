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


def log(msg: str):
    print(f"-------- {msg}")


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True)


def _call_capture(cmd: list[str], timeout: int = 120) -> str:
    try:
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


def clean_debate(text: str) -> str:
    s = re.sub(r"\s*/debate\b", "", text)
    s = re.sub(r"\s*--debate\b", "", s)
    return s.strip()


def run_debate(topic: str, rounds: int = 10) -> int:
    if not shutil.which("codex"):
        print("❌ Debate mode requires 'codex' CLI on PATH.")
        return 1

    # Prefer alternating models if available: CRITIC=codex, CREATOR=claude (fallback codex)
    have_claude = bool(shutil.which("claude"))

    def call_codex(prompt: str) -> str:
        return _call_capture(["codex", "exec", "-c", "model_reasoning_effort=high", prompt])

    def call_claude(prompt: str) -> str:
        if not have_claude:
            return call_codex(prompt)
        return _call_capture(["claude", "--model", "claude-sonnet-4-20250514", "-p", prompt], timeout=90)

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
        return t.strip()

    def build_prompt(role: str, other_text: str, i: int, n: int) -> str:
        if role == "CRITIC":
            sys_rules = (
                "You are CODEX-CRITIC: a rigorous, logic-first debater.\n"
                "RULES: output ONLY the CRITIC message, not both sides; do not summarize; do not write as CREATOR.\n"
                "FORMAT: begin with 'CRITIC: ' then the message (max 10 lines).\n"
                "TASK: Point out flaws, missing assumptions, risks; propose 1-2 concrete validations."
            )
            ctx = f"Round {i}/{n} — Topic: {topic}\nCREATOR said: {other_text or '(first turn)'}"
        else:
            sys_rules = (
                "You are CURSOR-CREATOR: a positive, creative collaborator.\n"
                "RULES: output ONLY the CREATOR message; do not imitate CRITIC; no summaries.\n"
                "FORMAT: begin with 'CREATOR: ' then the message (max 10 lines).\n"
                "TASK: Build constructively on CRITIC, propose improved approach and small actionable steps."
            )
            ctx = f"Round {i}/{n} — Topic: {topic}\nCRITIC said: {other_text}"
        return f"{sys_rules}\n\nCONTEXT:\n{ctx}"

    print("-------- Debate start (/debate): CODEX-CRITIC ↔ CURSOR-CREATOR")
    critic_last = ""
    transcript: list[str] = []
    for i in range(1, rounds + 1):
        # CRITIC turn (codex)
        c_prompt = build_prompt("CRITIC", critic_last, i, rounds)
        c_out_raw = call_codex(c_prompt) or "(no output)"
        c_out = only_role("CRITIC", c_out_raw)
        print(f"\n[Turn {i} — CODEX-CRITIC]\n{c_out}\n")
        transcript.append(f"[Turn {i} — CODEX-CRITIC]\n{c_out}\n")

        # CREATOR turn (claude if available, else codex)
        k_prompt = build_prompt("CREATOR", c_out, i, rounds)
        k_out_raw = call_claude(k_prompt) or "(no output)"
        k_out = only_role("CREATOR", k_out_raw)
        print(f"[Turn {i} — CURSOR-CREATOR]\n{k_out}\n")
        transcript.append(f"[Turn {i} — CURSOR-CREATOR]\n{k_out}\n")
        critic_last = k_out

    # Final synthesis via codex (or claude if available)
    fin = (
        "Synthesize the best combined outcome from the debate transcript. "
        "Provide a concise final recommendation with a 5-step plan and checks.\n\n"
        + "\n".join(transcript[-6:])
    )
    final_out = call_claude(fin) if have_claude else call_codex(fin)
    final_out = final_out or "(no output)"
    print("[Final Synthesis]\n" + final_out + "\n")
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
    if len(argv) <= 1:
        print("❌ Usage: tag-executor.py \"your question /tag\"")
        print("\n📋 Available Tags:")
        print("  /frontend-ultra, /frontend, /backend, /analyzer, /architect, /high, /seq, /seq-ultra, /debate")
        print("  SDD: sdd spec|plan|tasks|implement <text>")
        return 1

    text = " ".join(argv[1:]).strip()

    # Debate mode
    if is_debate(text):
        topic = clean_debate(text)
        return run_debate(topic, rounds=10)

    # SDD helpers
    if text.lower().startswith("sdd "):
        rc = run_sdd(text)
        if rc in (0, 1):
            return rc

    # Fallback: forward to optimize path (persona tags included in text)
    return run_optimize(text)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
