#!/usr/bin/env python3
"""
Reasoning Delegate - Offloads deep reasoning/planning to Codex (GPT-5)

Uses `codex exec -c reasoning_effort=high` when available, with fallbacks to
`codex --model gpt-5 -c model_reasoning_effort=high` and the local wrappers.

The prompt is engineered to trigger deep internal reasoning but to OUTPUT ONLY a
strict JSON plan schema we can parse and then execute. Chain-of-thought is not
exposed to the user-facing output; we only consume the final plan.
"""

from __future__ import annotations
import os
import json
import shlex
import subprocess
from typing import Any, Dict, Optional
import re


class ReasoningDelegate:
    """Utility to request a high-quality execution plan from Codex (GPT-5)."""

    def __init__(self) -> None:
        self.cmd_candidates = [
            lambda prompt: ["codex", "exec", "-c", "reasoning_effort=high", prompt],
            lambda prompt: ["codex", "--model", "gpt-5", "-c", "model_reasoning_effort=high", prompt],
            lambda prompt: ["bin/codex-high", prompt],
            lambda prompt: ["npm", "run", "codex:plan", "--silent", "--", prompt],
        ]

    def request_plan(self, prompt: str, timeout: int = 120) -> Dict[str, Any]:
        """
        Execute Codex with high reasoning to obtain a structured plan.
        Returns dict with keys: ok(bool), plan(dict|None), raw(str), error(str|None)
        """
        # Ensure codex CLI is installed/updated to latest before any execution
        self._ensure_codex_latest()
        last_err = None
        for build in self.cmd_candidates:
            cmd = build(prompt)
            try:
                proc = subprocess.run(
                    cmd, check=False, capture_output=True, text=True, timeout=timeout
                )
                stdout = proc.stdout or ""
                stderr = proc.stderr or ""
                if proc.returncode != 0 and not stdout.strip():
                    last_err = f"command failed rc={proc.returncode}, stderr={stderr[:2000]}"
                    continue

                plan = self._extract_json(stdout)
                if plan is not None:
                    return {"ok": True, "plan": plan, "raw": stdout, "error": None}
                # If no JSON found, still return raw for visibility to caller
                return {"ok": True, "plan": None, "raw": stdout, "error": None}
            except FileNotFoundError as e:
                last_err = str(e)
                continue
            except subprocess.TimeoutExpired:
                last_err = "timeout"
                continue

        return {"ok": False, "plan": None, "raw": "", "error": last_err or "all candidates failed"}

    def build_plan_prompt(
        self,
        persona_name: str,
        user_input: str,
        global_rules: Optional[str] = None,
    ) -> str:
        """
        Build a plan-first prompt designed to induce deep internal reasoning
        while asking the model to output only a strict JSON plan.
        """
        rules = global_rules or ""
        return f"""
You are GPT-5 Strategic Planner assisting the {persona_name} persona.
Think step-by-step internally to design a high-quality, actionable plan.
Do NOT reveal chain-of-thought. Output MUST be valid JSON only, following schema.

CONTEXT_RULES:
{rules}

USER_REQUEST:
{user_input}

SCHEMA (strict JSON):
{{
  "goal": "short goal statement",
  "assumptions": ["..."],
  "plan": "one paragraph plan overview",
  "steps": [
    {{
      "id": "S1",
      "title": "...",
      "rationale": "concise reasoning (no CoT)",
      "actions": ["shell or edit actions if any"],
      "expected_result": "..."
    }}
  ],
  "risks": ["..."],
  "validation": ["tests/verification steps"],
  "rollback": ["if applicable"],
  "notes": ["tips or references"]
}}

Return only JSON. No preface, no markdown, no explanation.
"""

    def _extract_json(self, s: str) -> Optional[Dict[str, Any]]:
        """Extract first JSON object from text (handles ``` fences)."""
        if not s:
            return None

        # Try direct parse first
        s_stripped = s.strip()
        try:
            return json.loads(s_stripped)
        except Exception:
            pass

        # Look for fenced code blocks
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", s, re.IGNORECASE)
        if fence_match:
            block = fence_match.group(1).strip()
            try:
                return json.loads(block)
            except Exception:
                pass

        # Try to find first JSON object heuristically
        obj_match = re.search(r"\{[\s\S]*\}", s)
        if obj_match:
            candidate = obj_match.group(0)
            try:
                return json.loads(candidate)
            except Exception:
                return None
        return None

    def _ensure_codex_latest(self) -> None:
        """Install or upgrade @openai/codex to latest via npm before use.

        Best-effort: if npm is missing or install fails, we log and continue to
        try executing anyway (fallbacks may still succeed)."""
        try:
            # Check npm availability
            proc = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=False)
            if proc.returncode != 0:
                print("-------- npm not found; skipping codex update")
                return

            print("-------- Ensuring @openai/codex@latest is installed (npm -g)")
            upd = subprocess.run(
                ["npm", "install", "-g", "@openai/codex@latest"],
                capture_output=True,
                text=True,
                check=False,
                timeout=300,
            )
            if upd.returncode == 0:
                print("-------- Codex CLI updated to latest")
            else:
                # Log shortened error to avoid noise
                msg = (upd.stderr or upd.stdout or "").strip().splitlines()[-1:] or ["unknown error"]
                print(f"-------- Codex update warning: {msg[0]}")
        except subprocess.TimeoutExpired:
            print("-------- Codex update timed out; continuing")
        except Exception as e:
            print(f"-------- Codex update error: {e}")
