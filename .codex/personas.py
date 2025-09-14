
#!/usr/bin/env python3
# Codex Personas Helper — programmatic prompt builders (English only).
from textwrap import dedent

def build_debate_prompt(topic: str, rounds: int = 8) -> str:
    rounds = max(2, min(int(rounds or 8), 20))
    return dedent(f'''    You are a single model simulating a structured internal debate with two clearly separated selves:
    - Positive Self (Builder): constructive, solution-focused.
    - Critical Self (Skeptic): risk-driven, assumption-testing.

    Rules:
    - English only. Keep each turn concise (<= 6 lines).
    - Alternate strictly: Positive → Critical → Positive → ... ({rounds} rounds).
    - No repetition; each turn must add new reasoning.
    - End with a Synthesis that integrates strengths + mitigations.

    Topic: {topic}

    Output template:
    [INTENT]
    - Debate: {topic}
    [TASK_CLASSIFY]
    - Class: H (multi-step reasoning & evaluation)
    [PLAN]
    - Rounds: {rounds}
    - Criteria: correctness, risks, minimal viable path
    [EXECUTE]
    1) Positive Self: ...
    2) Critical Self: ...
    ... (continue alternating up to {rounds})
    [VERIFY]
    - Checks: factuality, feasibility, risk coverage
    [REPORT]
    - Synthesis: final position, plan, and guardrails
    ''')

def build_persona_prompt(name: str, query: str, context: str = "") -> str:
    # Return a minimal persona-wrapped prompt.
    header = f"**[Persona]** {name}

"
    return header + (context or "") + f"

**[User's Request]**
{query}
"
