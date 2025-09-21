from typing import Literal, Optional

ReasoningLevel = Literal["medium","high"]
TaskClass = Literal["L0","L1","H"]

H_PATTERNS = [
    r"architecture|design(?!\s*small)|hexagonal|domain model|DDD",
    r"security|CWE|auth(entication|orization)|RBAC|secret|XSS|SQLi",
    r"performance|profil(ing)?|latency|p95|throughput|memory",
    r"debug(ging)?|root\s*cause|unknown\s*error|flaky",
    r"migration|backfill|data model",
    r"shopify|rate limit|idempotency|backoff",
    r"cross-?module|monorepo|multi-?module",
]

def classify_task(text: str) -> TaskClass:
    import re
    s = (text or "")[:4000]
    if any(re.search(rx, s, re.I) for rx in H_PATTERNS):
        return "H"
    if re.search(r"\b(test|jest|unit|integration|type(s)?|migration)\b", s, re.I):
        return "L1"
    if re.search(r"\b(lint|format|rename|prettier|eslint|find[- ]?replace|small refactor)\b", s, re.I):
        return "L0"
    return "L1"

def decide_switch(current: ReasoningLevel, cls: TaskClass) -> dict:
    if cls == "H" and current != "high":
        return {"switch": "high", "reason": "deep_planning"}
    if cls != "H" and current != "medium":
        return {"switch": "medium", "reason": "execution"}
    return {}

