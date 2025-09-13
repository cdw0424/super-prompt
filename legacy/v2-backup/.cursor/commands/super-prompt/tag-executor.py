#!/usr/bin/env python3
import os, re, sys, shutil, subprocess

def _run(cmd):
    return subprocess.run(cmd, text=True)

def _cap(cmd, timeout=120):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (p.stdout or "").strip()
    except Exception:
        return ""

def optimize(text: str) -> int:
    if shutil.which("super-prompt"):
        return _run(["super-prompt","optimize", text]).returncode
    return _run(["npx","@cdw0424/super-prompt","optimize", text]).returncode

def is_debate(text:str)->bool:
    return "/debate" in text or " --debate" in text

def clean_debate(text:str)->str:
    s=re.sub(r"\s*/debate","",text)
    s=re.sub(r"\s*--debate","",s)
    return s.strip()

    def debate(topic:str, rounds:int=10)->int:
        if not shutil.which("codex"):
            print("❌ Debate mode requires 'codex' CLI on PATH."); return 1
        have_claude = bool(shutil.which("claude"))
        def call_codex(p: str)->str:
            return _cap(["codex","exec","-c","model_reasoning_effort=high", p])
        def call_claude(p: str)->str:
            if not have_claude: return call_codex(p)
            return _cap(["claude","--model","claude-sonnet-4-20250514","-p", p], timeout=90)
        def only_role(role:str, text:str)->str:
            t=text.strip()
            t=re.sub(r"^```[a-zA-Z]*|```$","",t,flags=re.M)
            other="CREATOR" if role=="CRITIC" else "CRITIC"
            m=re.search(rf"^\s*{other}\s*:|^\s*{other}", t, flags=re.I|re.M)
            if m: t=t[:m.start()].rstrip()
            t=re.sub(rf"^\s*{role}\s*:\s*","",t,flags=re.I)
            return t.strip()
        def build(role:str, other:str, i:int, n:int, initial:bool=False)->str:
            shared=(
                "HARD CONSTRAINTS (read carefully):
"
                "- Output ONLY the {role} message for THIS TURN.
"
                "- NEVER include both roles in one answer.
"
                "- NO summaries or final conclusions before the end.
"
                "- DO NOT simulate the other role.
"
                "- LIMIT to 10 non-empty lines, no code fences, no headings.
"
                "- Begin the first line with '{role}: ' then the content.
"
            )
            if role=="CRITIC":
                sys=("You are CODEX-CRITIC: rigorous, logic-first.
"+shared.format(role="CRITIC")+
                     "TASK: flaws, missing assumptions, risks; 1-2 testable validations.")
                ctx=f"Round {i}/{n} — Topic: {topic}
CREATOR said: {other or '(first turn)'}"
            else:
                sys=("You are CURSOR-CREATOR: positive, creative.
"+shared.format(role="CREATOR")+
                     "TASK: build constructively; propose improved approach + small steps.")
                if initial:
                    ctx=f"Round {i}/{n} — Topic: {topic}
FRAMING: Provide an initial stance and 2-3 small steps."
                else:
                    ctx=f"Round {i}/{n} — Topic: {topic}
CRITIC said: {other}"
            return f"{sys}

CONTEXT:
{ctx}"
        print("-------- Debate start (/debate): CURSOR-CREATOR ↔ CODEX-CRITIC")
        tr=[]; last_creator=""; last_critic=""
        for i in range(1, rounds+1):
            k_raw=call_claude(build("CREATOR", last_critic, i, rounds, initial=(i==1))) or "(no output)"
            k_out=only_role("CREATOR", k_raw)
            print(f"
[Turn {i} — CURSOR-CREATOR]
{k_out}
"); tr.append(f"[Turn {i} — CURSOR-CREATOR]
{k_out}
"); last_creator=k_out
            c_raw=call_codex(build("CRITIC", last_creator, i, rounds)) or "(no output)"
            c_out=only_role("CRITIC", c_raw)
            print(f"[Turn {i} — CODEX-CRITIC]
{c_out}
"); tr.append(f"[Turn {i} — CODEX-CRITIC]
{c_out}
"); last_critic=c_out
        fin=("Synthesize the best combined outcome; provide final recommendation with short 5-step plan and checks.

"+"
".join(tr[-6:]))
        fo=(call_claude(fin) if have_claude else call_codex(fin)) or "(no output)"
        print("[Final Synthesis]
"+fo+"
"); return 0


SDD_RE=re.compile(r"^sdd\s+(spec|plan|tasks|implement)\s*(.*)$", re.I)

def sdd(text:str)->int:
    m=SDD_RE.match(text.strip())
    if not m: return 2
    sub=m.group(1).lower(); body=(m.group(2) or "").strip()
    if sub=="spec":
        hdr=("[SDD SPEC REQUEST]
- 문제정의/배경
- 목표/가치
- 성공 기준(정량/정성)
- 범위/비범위
- 제약/가정
- 이해관계자/의존성
- 상위 수준 아키텍처
- 수용 기준 초안
[주의] 스택/벤더 확정 금지, 간결/구조화")
        return optimize(f"{hdr}

[사용자 요청]
{body} /architect")
    if sub=="plan":
        hdr=("[SDD PLAN REQUEST]
- 구성요소/책임
- 데이터/계약(API·이벤트)
- 단계별 구현(작은 스텝)
- 리스크/대안/롤백
- 비기능(보안/성능/관측성)
- 수용 기준 체크리스트")
        return optimize(f"{hdr}

[사용자 요청]
{body} /architect")
    if sub=="tasks":
        hdr=("[SDD TASKS REQUEST]
- [TASK-ID] 제목
  - 설명
  - 산출물
  - 수용 기준
  - 예상치/우선순위/의존성
[주의] 최소 변경/독립 검증")
        return optimize(f"{hdr}

[사용자 요청]
{body} /analyzer")
    if sub=="implement":
        hdr=("[SDD IMPLEMENT REQUEST]
- 변경 파일 개요
- 단계별 적용(작은 커밋/롤백)
- 리스크와 대응
- 검증(테스트/검수)
[주의] 범위 밖 변경 금지, 기존 패턴 우선")
        return optimize(f"{hdr}

[사용자 요청]
{body} /architect")
    return 2

def main(argv:list[str])->int:
    if len(argv)<=1:
        print("❌ Usage: tag-executor.py "your question /tag"

SDD: sdd spec|plan|tasks|implement <text>
Debate: append /debate"); return 1
    text=" ".join(argv[1:]).strip()
    if is_debate(text):
        return debate(clean_debate(text), 10)
    if text.lower().startswith("sdd "):
        rc=sdd(text)
        if rc in (0,1): return rc
    return optimize(text)

if __name__=="__main__":
    sys.exit(main(sys.argv))
