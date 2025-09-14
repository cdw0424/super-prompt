#!/usr/bin/env python3
"""
ReasoningDelegate — bridges to Codex CLI for planning/execution when deep reasoning is needed.

Design goals:
- No external Python deps. Pure stdlib.
- Prefer repo-local wrappers when available (bin/codex-high, bin/codex-medium).
- Fall back to global `codex` if wrappers absent.
- Return structured results (JSON plan when requested).
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any


class ReasoningDelegate:
    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root)

    def _bootstrap_prompt(self) -> str:
        # Prefer project prompt file if present
        file_path = self.project_root / 'prompts' / 'codex_amr_bootstrap_prompt_en.txt'
        try:
            if file_path.exists():
                return file_path.read_text(encoding='utf-8')
        except Exception:
            pass
        # Minimal inline fallback
        return (
            "You are a coding agent with an Auto Model Router (AMR).\n"
            "- Language: English. Logs start with '--------'.\n"
            "- State machine per turn: [INTENT]→[TASK_CLASSIFY]→[PLAN]→[EXECUTE]→[VERIFY]→[REPORT].\n"
            "- Switch to high for planning/review of heavy tasks; execute at medium.\n"
        )

    def _find_codex_bin(self, level: str) -> Optional[str]:
        # Try repo-local wrappers
        candidate = self.project_root / 'bin' / (f'codex-{level}' if level in { 'high', 'medium' } else 'codex-high')
        if candidate.exists():
            return str(candidate)
        # Fallback to global codex
        return 'codex'

    def _run_codex(self, prompt: str, level: str = 'high', timeout: int = 300) -> Tuple[int, str, str]:
        exe = self._find_codex_bin(level)
        env = os.environ.copy()
        try:
            # Pass prompt as a single argument; many codex CLIs accept it directly.
            # If not, the user can adjust their CLI; we keep stdin fallback for portability.
            cmd = [exe, prompt]
            proc = subprocess.run(cmd, check=False, text=True, capture_output=True, timeout=timeout, env=env)
            if (proc.returncode != 0) or (not (proc.stdout or '').strip()):
                # stdin fallback
                proc = subprocess.run([exe], input=prompt, check=False, text=True, capture_output=True, timeout=timeout, env=env)
            return proc.returncode, proc.stdout or '', proc.stderr or ''
        except Exception as e:
            return 1, '', f'{e}'

    def build_plan_prompt(self, persona_name: str, user_input: str, global_rules: str) -> str:
        bootstrap = self._bootstrap_prompt()
        return (
            f"{bootstrap}\n\n"
            f"[INTENT]\n- Plan at high reasoning for: {persona_name}\n\n"
            f"[TASK_CLASSIFY]\n- Class: H (deep planning)\n\n"
            f"[PLAN]\n"
            f"- Use the following rules:\n{global_rules}\n\n"
            f"- Create a concise JSON plan with keys: goal, plan (bullets), risks, test, rollback.\n"
            f"- JSON only. No markdown/code fences.\n\n"
            f"[USER_INPUT]\n{user_input}\n\n"
            f"[OUTPUT]\nJSON only."
        )

    def request_plan(self, prompt: str, timeout: int = 300) -> Dict[str, Any]:
        code, out, err = self._run_codex(prompt, level='high', timeout=timeout)
        if code != 0:
            return { 'ok': False, 'error': f'codex failed (exit={code}): {err.strip()}' }
        # Try to locate JSON in output
        text = (out or '').strip()
        # Strip code fences if present
        if text.startswith('```'):
            text = text.strip('`')
        # Attempt JSON parse; if fails, wrap into a simple plan
        try:
            data = json.loads(text)
            return { 'ok': True, 'plan': data, 'raw': text }
        except Exception:
            plan = {
                'goal': 'Execute user request effectively',
                'plan': [text[:8000]],
                'risks': ['Plan not in JSON; using raw output as plan note'],
                'test': 'Run verification steps described in the output',
                'rollback': 'Revert any changes made during execution'
            }
            return { 'ok': True, 'plan': plan, 'raw': text }

    def exec_prompt(self, system_prompt: str, timeout: int = 600, level: str = 'medium') -> Dict[str, Any]:
        # Execute engineered prompt at chosen reasoning level
        code, out, err = self._run_codex(system_prompt, level=level, timeout=timeout)
        return { 'ok': code == 0, 'stdout': out, 'stderr': err, 'exit': code }

