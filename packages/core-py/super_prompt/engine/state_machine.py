from typing import List, Literal

Step = Literal["INTENT","TASK_CLASSIFY","PLAN","EXECUTE","VERIFY","REPORT"]

STEPS: List[Step] = [
    "INTENT",
    "TASK_CLASSIFY",
    "PLAN",
    "EXECUTE",
    "VERIFY",
    "REPORT",
]

