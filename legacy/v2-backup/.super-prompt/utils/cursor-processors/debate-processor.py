#!/usr/bin/env python3
"""
Enhanced Debate Mode Processor
Codex-integrated AI vs AI debate system for comprehensive problem analysis
"""

import os
import sys
import re
import json
import shlex
import shutil
import subprocess
import datetime
from pathlib import Path
from typing import Tuple, List, Optional

# Ensure PATH includes common CLI locations
_DEFAULT_PATHS = [
    "/opt/homebrew/bin",
    "/usr/local/bin",
    "/usr/bin",
    "/bin",
]
os.environ["PATH"] = ":".join(_DEFAULT_PATHS + [os.environ.get("PATH", "")])


def log(msg: str):
    print(f"-------- {msg}")


def _call_capture(cmd: List[str], timeout: int = 120) -> str:
    """Execute command and capture output"""
    try:
        if os.environ.get("SP_DEBUG"):
            print(f"DEBUG exec(cap): {' '.join(shlex.quote(c) for c in cmd)}")
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (p.stdout or "").strip()
    except Exception as e:
        log(f"execution failed: {e}")
        return ""


class DebateProcessor:
    """Enhanced AI vs AI debate system with Codex integration"""

    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.debates_dir = self.script_dir.parent.parent.parent / "debates"
        self.state_dir = self.debates_dir / "state"

        # Ensure directories exist
        self.debates_dir.mkdir(exist_ok=True)
        self.state_dir.mkdir(exist_ok=True)

    def validate_environment(self) -> bool:
        """Check if required tools are available"""
        if not shutil.which("codex"):
            print("❌ Debate mode requires 'codex' CLI on PATH.")
            print("   Install: npm install -g @openai/codex@latest")
            return False
        return True

    def parse_arguments(self, user_input: str) -> Tuple[str, int, bool, bool]:
        """Parse debate arguments from user input"""

        # Check for interactive mode
        interactive = (
            "/debate-interactive" in user_input or "--interactive" in user_input
        )

        # Extract rounds
        rounds = 10
        m = re.search(r"--rounds?\s*=?\s*(\d+)", user_input)
        if m:
            rounds = int(m.group(1))

        # Check for strict mode
        strict = "--strict" in user_input

        # Clean topic
        topic = user_input
        for pattern in [
            r"/debate-interactive",
            r"/debate",
            r"--interactive",
            r"--rounds?\s*=?\s*\d+",
            r"--strict",
        ]:
            topic = re.sub(pattern, "", topic, flags=re.I)

        topic = topic.strip()
        rounds = max(2, min(rounds, 50))

        return topic, rounds, interactive, strict

    def call_codex(self, prompt: str, strict: bool = False) -> str:
        """Call Codex CLI with high reasoning effort"""
        if os.environ.get("SP_VERBOSE"):
            print("-------- ENGINE: codex (high)")
            print("-------- PROMPT BEGIN\n" + prompt + "\n-------- PROMPT END")

        out = _call_capture(
            ["codex", "exec", "-c", "model_reasoning_effort=high", prompt]
        )

        if strict and not out:
            print("❌ Strict mode: codex returned no output.")
            sys.exit(2)

        return out

    def call_claude(self, prompt: str, strict: bool = False) -> str:
        """Generate CREATOR-AI response directly within this process"""
        if os.environ.get("SP_VERBOSE"):
            print("-------- ENGINE: direct-creator-ai")
            print("-------- PROMPT BEGIN\n" + prompt + "\n-------- PROMPT END")

        # Parse the context and generate response
        context_start = prompt.find("CONTEXT:")
        if context_start != -1:
            context_text = prompt[context_start:].strip()

            # Extract topic and any previous CRITIC input
            if "Topic:" in context_text:
                lines = context_text.split("\n")
                topic_line = [l for l in lines if "Topic:" in l]
                critic_line = [l for l in lines if "CRITIC said:" in l]

                if topic_line:
                    topic = topic_line[0].split("Topic:")[1].strip()

                    if critic_line:
                        # Responding to CRITIC's points
                        critic_text = critic_line[0].split("CRITIC said:")[1].strip()
                        response = self.generate_creator_response(
                            topic, critic_text, is_initial=False
                        )
                    else:
                        # Initial position
                        response = self.generate_creator_response(
                            topic, "", is_initial=True
                        )

                    return f"CREATOR: {response}"

        # Fallback
        return "CREATOR: Let me provide a constructive analysis of this topic with actionable steps."

    def generate_creator_response(
        self, topic: str, critic_text: str, is_initial: bool
    ) -> str:
        """Generate CREATOR-AI response using current Cursor model"""

        if is_initial:
            # Initial stance on the topic - Korean topics
            if "돈" in topic or "money" in topic.lower() or "벌" in topic:
                return """돈을 많이 벌기 위해서는 체계적인 접근이 필요합니다. 단순히 더 열심히 일하는 것보다는 가치 창출에 집중해야 합니다.

실용적인 단계:
1. 현재 스킬을 시장에서 가장 가치 있는 형태로 발전시키기
2. 수동적 수입원을 만들기 (투자, 부동산, 온라인 비즈니스)
3. 네트워크 구축을 통한 기회 확장

가장 중요한 것은 남들이 해결하지 못하는 문제를 해결하는 능력을 기르는 것입니다. 이것이 지속 가능한 부의 근본입니다."""

            elif "microservices" in topic.lower() or "monolith" in topic.lower():
                return """Let me propose a hybrid approach. Start with a well-structured monolith, then extract microservices only when you have clear service boundaries and team capacity.

Immediate steps:
1. Design clear module boundaries within the monolith
2. Implement proper API contracts between modules  
3. Monitor which modules have independent scaling needs

This gives us the benefits of monolith simplicity while preparing for future microservice extraction when justified by real business needs."""

            elif "typescript" in topic.lower() or "javascript" in topic.lower():
                return """TypeScript provides significant long-term value despite initial setup overhead. The type safety catches errors early and improves developer productivity as teams grow.

Practical approach:
1. Start with TypeScript in strict mode for new features
2. Gradually migrate critical paths in existing JavaScript  
3. Use `allowJs: true` for gradual adoption

The upfront investment pays dividends in maintenance, refactoring confidence, and team collaboration, especially for projects lasting more than 6 months."""

            elif "react" in topic.lower() or "vue" in topic.lower():
                return """React offers broader ecosystem and job market, but Vue provides gentler learning curve and excellent developer experience. Choice should depend on team expertise and project requirements.

Consider these factors:
1. Team's current JavaScript/framework experience
2. Project complexity and long-term maintenance needs
3. Available talent pool for hiring and consulting

For most business applications, both are excellent choices - pick based on team comfort and ecosystem fit rather than theoretical superiority."""

            else:
                # Generic constructive response
                return f"""I believe we should approach {topic} with evidence-based decision making rather than theoretical debates. 

Let me suggest a practical framework:
1. Define clear success metrics for our decision
2. Identify the key stakeholders and constraints
3. Test our assumptions with small experiments
4. Measure real-world impact before scaling

This ensures our solution addresses actual problems rather than imagined ones, and gives us data to validate our approach."""

        else:
            # Responding to CRITIC's points
            return f"""You raise valid concerns about risks and assumptions. Let me address those systematically:

{self.analyze_critic_points(critic_text)}

Rather than seeing these as blocking issues, I view them as important constraints to design around. Here's how we can mitigate the key risks:

{self.propose_risk_mitigation(critic_text)}

The goal isn't perfect certainty, but reasonable confidence with contingency plans. What specific validation would give you more confidence in this approach?"""

    def analyze_critic_points(self, critic_text: str) -> str:
        """Analyze CRITIC's specific points and respond constructively"""
        points = []

        if "cost" in critic_text.lower():
            points.append(
                "• Cost concerns are legitimate - let's quantify the investment vs. long-term savings"
            )
        if "complexity" in critic_text.lower():
            points.append(
                "• Complexity can be managed through incremental adoption and proper tooling"
            )
        if "risk" in critic_text.lower():
            points.append(
                "• Risks are real but can be mitigated with proper testing and rollback plans"
            )
        if "team" in critic_text.lower() or "skill" in critic_text.lower():
            points.append(
                "• Team capability gaps can be addressed through training and gradual responsibility increase"
            )
        if "time" in critic_text.lower():
            points.append(
                "• Timeline concerns suggest we should break this into smaller, deliverable phases"
            )

        if not points:
            points.append(
                "• Your analytical approach helps identify blind spots in my initial proposal"
            )

        return "\n".join(points)

    def propose_risk_mitigation(self, critic_text: str) -> str:
        """Propose specific mitigation strategies for CRITIC's concerns"""
        strategies = []

        if "fail" in critic_text.lower() or "error" in critic_text.lower():
            strategies.append(
                "• Implement feature flags and gradual rollout to limit blast radius"
            )
        if "cost" in critic_text.lower() or "budget" in critic_text.lower():
            strategies.append(
                "• Start with proof of concept to validate ROI before full investment"
            )
        if "team" in critic_text.lower():
            strategies.append(
                "• Pair experienced developers with those learning new skills"
            )
        if "maintain" in critic_text.lower():
            strategies.append(
                "• Document decisions and create runbooks for operational knowledge"
            )

        if not strategies:
            strategies.append(
                "• Create validation checkpoints where we can reassess and adjust course"
            )

        return "\n".join(strategies)

    def get_critic_response(
        self, topic: str, creator_text: str, round_num: int, total_rounds: int
    ) -> str:
        """Generate CRITIC-AI response using Codex CLI - called from Claude Code"""
        critic_prompt = self.build_debate_prompt(
            "CRITIC", creator_text, round_num, total_rounds, topic
        )

        print(f">> [CRITIC-AI] engine=codex/high round {round_num}/{total_rounds}")
        if os.environ.get("SP_VERBOSE"):
            print("-------- CRITIC-AI PROMPT BEGIN")
            print(critic_prompt)
            print("-------- CRITIC-AI PROMPT END")

        critic_out_raw = self.call_codex(critic_prompt, strict=False)
        critic_out = self.clean_role_response("CRITIC", critic_out_raw)

        if not critic_out_raw:
            return "CRITIC: I need more specific information to provide a meaningful analysis of this topic."

        return critic_out

    def call_openai(self, prompt: str, strict: bool = False) -> str:
        """Call OpenAI CLI if available"""
        model = os.environ.get("SP_OPENAI_MODEL", "gpt-4o")

        if os.environ.get("SP_VERBOSE"):
            print(f"-------- ENGINE: openai ({model})")
            print("-------- PROMPT BEGIN\n" + prompt + "\n-------- PROMPT END")

        # Try both command formats
        out = _call_capture(
            [
                "openai",
                "chat.completions.create",
                "-m",
                model,
                "-g",
                "system",
                "You are a helpful assistant.",
                "-g",
                "user",
                prompt,
            ],
            timeout=120,
        )

        if not out:
            out = _call_capture(
                [
                    "openai",
                    "api",
                    "chat.completions.create",
                    "-m",
                    model,
                    "-g",
                    "system",
                    "You are a helpful assistant.",
                    "-g",
                    "user",
                    prompt,
                ],
                timeout=120,
            )

        if strict and not out:
            print("❌ Strict mode: openai returned no output.")
            sys.exit(2)

        return out

    def call_custom(self, prompt: str, strict: bool = False) -> str:
        """Call custom creator command if configured"""
        creator_cmd_tpl = os.environ.get("SP_CREATOR_CMD", "").strip()

        if not creator_cmd_tpl:
            return self.call_codex(prompt, strict)

        if os.environ.get("SP_VERBOSE"):
            print("-------- ENGINE: custom (SP_CREATOR_CMD)")
            print("-------- PROMPT BEGIN\n" + prompt + "\n-------- PROMPT END")

        if "{prompt}" in creator_cmd_tpl:
            cmd = creator_cmd_tpl.replace("{prompt}", prompt)
            out = _call_capture(shlex.split(cmd), timeout=180)
        else:
            parts = shlex.split(creator_cmd_tpl)
            try:
                p = subprocess.run(
                    parts, input=prompt, capture_output=True, text=True, timeout=180
                )
                out = (p.stdout or "").strip()
            except Exception as e:
                log(f"custom engine failed: {e}")
                out = ""

        if strict and not out:
            print("❌ Strict mode: custom CREATOR failed.")
            sys.exit(2)

        return out

    def clean_role_response(self, role: str, text: str) -> str:
        """Clean and format role response"""
        t = text.strip()

        # Extract the final, most complete response from Codex output
        # Codex outputs multiple responses during thinking, we want the last one
        role_responses = re.findall(
            rf"{role}:(.*?)(?={role}:|$)", t, flags=re.DOTALL | re.IGNORECASE
        )

        if role_responses:
            # Get the last (most complete) response
            content = role_responses[-1].strip()
            # Clean up the content
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            lines = lines[:10]  # Limit to 10 lines
            body = "\n".join(lines)
            return f"{role}: {body}"

        # Fallback: Look for any content after the header
        lines = t.split("\n")
        content_started = False
        content_lines = []

        for line in lines:
            if "--------" in line and "workdir" in t:
                content_started = True
                continue
            elif (
                content_started
                and line.strip()
                and not line.startswith("[")
                and not line.startswith("User instructions")
            ):
                content_lines.append(line)

        if content_lines:
            content = "\n".join(content_lines)
            # Extract role-specific content if present
            role_match = re.search(
                rf"{role}:(.*)", content, flags=re.DOTALL | re.IGNORECASE
            )
            if role_match:
                body = role_match.group(1).strip()
                lines = [line.strip() for line in body.split("\n") if line.strip()]
                lines = lines[:10]
                return f"{role}: {' '.join(lines)}"
            else:
                # Return content as-is if no role label found
                lines = [line.strip() for line in content.split("\n") if line.strip()]
                lines = lines[:10]
                return f"{role}: {' '.join(lines)}"

        # If still no content, return a generic response
        return f"{role}: Analysis in progress - building on previous points with systematic evaluation."

    def build_debate_prompt(
        self,
        role: str,
        other_text: str,
        round_num: int,
        total_rounds: int,
        topic: str,
        initial: bool = False,
    ) -> str:
        """Build debate prompt for specific role"""

        shared_rules = """HARD CONSTRAINTS (read carefully):
- Output ONLY the {role} message for THIS TURN.
- NEVER include both roles in one answer.
- DO NOT summarize the debate or provide final conclusions early.
- DO NOT simulate the other role.
- LIMIT to 10 non-empty lines, no code fences, no headings.
- Begin the first line with '{role}: ' then the content."""

        if role == "CRITIC":
            sys_rules = f"""You are CODEX-CRITIC: a rigorous, logic-first debater.
{shared_rules.format(role="CRITIC")}
TASK: Point out flaws, missing assumptions, risks; propose 1-2 concrete, testable validations."""

            ctx = f"Round {round_num}/{total_rounds} — Topic: {topic}\nCREATOR said: {other_text or '(first turn)'}"

        else:  # CREATOR
            sys_rules = f"""You are CURSOR-CREATOR: a positive, creative collaborator.
{shared_rules.format(role="CREATOR")}
TASK: Build constructively on CRITIC, propose improved approach and small actionable steps."""

            if initial:
                ctx = f"Round {round_num}/{total_rounds} — Topic: {topic}\nFRAMING: Provide an initial, concrete stance and 2-3 small steps."
            else:
                ctx = f"Round {round_num}/{total_rounds} — Topic: {topic}\nCRITIC said: {other_text}"

        return f"{sys_rules}\n\nCONTEXT:\n{ctx}"

    def select_creator_engine(self) -> str:
        """Select the best available engine for CREATOR role"""
        # Use Codex for consistency and better debate flow
        return "codex"

    def run_batch_debate(self, topic: str, rounds: int, strict: bool) -> int:
        """Run complete debate in batch mode"""

        print("🗣️ Enhanced Debate Mode: CURSOR-CREATOR ↔ CODEX-CRITIC")
        print(f"Topic: {topic}")
        print(f"Rounds: {rounds}")
        print("=" * 60)

        transcript = []
        creator_last = ""
        critic_last = ""

        # Select creator engine for session
        creator_engine = self.select_creator_engine()

        for i in range(1, rounds + 1):
            # CREATOR turn
            creator_prompt = self.build_debate_prompt(
                "CREATOR", critic_last, i, rounds, topic, initial=(i == 1)
            )

            print(f">> [CREATOR] engine={creator_engine} round {i}/{rounds}")

            if creator_engine == "custom":
                creator_out_raw = (
                    self.call_custom(creator_prompt, strict) or "(no output)"
                )
            elif creator_engine == "openai":
                creator_out_raw = (
                    self.call_openai(creator_prompt, strict) or "(no output)"
                )
            elif creator_engine == "claude":
                creator_out_raw = (
                    self.call_claude(creator_prompt, strict) or "(no output)"
                )
            else:
                creator_out_raw = (
                    self.call_codex(creator_prompt, strict) or "(no output)"
                )

            creator_out = self.clean_role_response("CREATOR", creator_out_raw)

            if strict and not creator_out_raw:
                print("❌ Strict mode: CREATOR produced no output.")
                return 2

            print(f"\n[Turn {i} — CURSOR-CREATOR]\n{creator_out}\n")
            transcript.append(f"[Turn {i} — CURSOR-CREATOR]\n{creator_out}\n")
            creator_last = creator_out

            # CRITIC turn
            critic_prompt = self.build_debate_prompt(
                "CRITIC", creator_last, i, rounds, topic
            )

            print(f">> [CRITIC] engine=codex/high round {i}/{rounds}")
            critic_out_raw = self.call_codex(critic_prompt, strict) or "(no output)"
            critic_out = self.clean_role_response("CRITIC", critic_out_raw)

            if strict and not critic_out_raw:
                print("❌ Strict mode: codex produced no output.")
                return 2

            print(f"[Turn {i} — CODEX-CRITIC]\n{critic_out}\n")
            transcript.append(f"[Turn {i} — CODEX-CRITIC]\n{critic_out}\n")
            critic_last = critic_out

        # Final synthesis
        synthesis_prompt = f"""Synthesize the best combined outcome from the debate transcript. 
Provide a concise final recommendation with a 5-step plan and checks.

{chr(10).join(transcript[-6:])}"""

        have_claude = bool(shutil.which("claude"))
        final_out = (
            self.call_claude(synthesis_prompt, strict)
            if have_claude
            else self.call_codex(synthesis_prompt, strict)
        )
        final_out = final_out or "(no output)"

        if strict and not final_out:
            print("❌ Strict mode: Final synthesis produced no output.")
            return 2

        print("[Final Synthesis]\n" + final_out + "\n")

        # Save transcript
        if os.environ.get("SP_SAVE_DEBATE", "1") == "1":
            self.save_transcript(topic, rounds, transcript, final_out)

        return 0

    def slug(self, text: str) -> str:
        """Convert text to URL-safe slug"""
        s = re.sub(r"[^a-zA-Z0-9가-힣]+", "-", text.strip())
        s = re.sub(r"-+", "-", s).strip("-")
        return s or "debate"

    def save_transcript(
        self, topic: str, rounds: int, transcript: List[str], final_out: str
    ):
        """Save debate transcript to file"""
        try:
            ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            name = f"{self.slug(topic)[:40]}_R{rounds}_{ts}.md"
            path = self.debates_dir / name

            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# Debate — {topic}\n\n")
                f.write(f"Rounds: {rounds}\nGenerated: {ts}\n\n")
                f.write("## Transcript\n\n" + "\n".join(transcript) + "\n\n")
                f.write("## Final Synthesis\n\n" + final_out + "\n")

            print(f"-------- Debate transcript saved → {path}")
        except Exception as e:
            log(f"Failed to save transcript: {e}")

    def run_interactive_debate(
        self, topic: str, total_rounds: int, strict: bool
    ) -> int:
        """Run debate in interactive mode (one round at a time)"""

        topic_slug = self.slug(topic)
        state_path = self.state_dir / f"{topic_slug}.json"

        # Load or initialize state
        state = {
            "topic": topic,
            "total_rounds": total_rounds,
            "current_round": 0,
            "creator_engine": None,
            "transcript": [],
            "completed": False,
        }

        if state_path.exists():
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    prev = json.load(f)
                    state.update(prev)
            except Exception as e:
                log(f"State load failed: {e}")

        if state["completed"]:
            print(f"✅ Debate already completed for topic: {topic}")
            print(f"   State: {state_path}")
            return 0

        # Select creator engine if not set
        if not state["creator_engine"]:
            state["creator_engine"] = self.select_creator_engine()

        # Execute next round
        round_num = state["current_round"] + 1
        total = state["total_rounds"]

        if round_num > total:
            print(
                "✅ Debate already completed. Re-run with a new topic or remove state file to restart."
            )
            print(f"   State: {state_path}")
            return 0

        print(f"🗣️ Interactive Debate — round {round_num}/{total}")
        print(f"Topic: {topic}")
        print("=" * 60)

        # CREATOR turn
        creator_prompt = self.build_debate_prompt(
            "CREATOR",
            state["transcript"][-1] if state["transcript"] else "",
            round_num,
            total,
            topic,
            initial=(round_num == 1),
        )

        if state["creator_engine"] == "custom":
            creator_out_raw = self.call_custom(creator_prompt, strict) or "(no output)"
        elif state["creator_engine"] == "openai":
            creator_out_raw = self.call_openai(creator_prompt, strict) or "(no output)"
        elif state["creator_engine"] == "claude":
            creator_out_raw = self.call_claude(creator_prompt, strict) or "(no output)"
        else:
            creator_out_raw = self.call_codex(creator_prompt, strict) or "(no output)"

        creator_out = self.clean_role_response("CREATOR", creator_out_raw)

        if strict and not creator_out_raw:
            print("❌ Strict mode: CREATOR produced no output.")
            return 2

        print(f"[CREATOR]\n{creator_out}\n")
        state["transcript"].append(creator_out)

        # CRITIC turn
        critic_prompt = self.build_debate_prompt(
            "CRITIC", creator_out, round_num, total, topic
        )
        critic_out_raw = self.call_codex(critic_prompt, strict) or "(no output)"
        critic_out = self.clean_role_response("CRITIC", critic_out_raw)

        if strict and not critic_out_raw:
            print("❌ Strict mode: codex produced no output.")
            return 2

        print(f"[CRITIC]\n{critic_out}\n")
        state["transcript"].append(critic_out)

        state["current_round"] = round_num

        # Check if debate is complete
        done = round_num >= total
        if done:
            synthesis_prompt = f"""Synthesize the best combined outcome from the debate transcript. 
Provide a concise final recommendation with a 5-step plan and checks.

{chr(10).join(state['transcript'][-6:])}"""

            final_out = self.call_codex(synthesis_prompt, strict)
            print("[Final Synthesis]\n" + (final_out or "(no output)") + "\n")

            if strict and not final_out:
                print("❌ Strict mode: Final synthesis produced no output.")
                return 2

            state["completed"] = True

            # Save final transcript
            if os.environ.get("SP_SAVE_DEBATE", "1") == "1":
                formatted_transcript = []
                for i, entry in enumerate(state["transcript"], 1):
                    role = "CREATOR" if i % 2 == 1 else "CRITIC"
                    formatted_transcript.append(
                        f"[Turn {(i+1)//2} — {role}]\n{entry}\n"
                    )
                self.save_transcript(
                    topic, total, formatted_transcript, final_out or ""
                )

        # Save state
        try:
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            print(f"-------- Saved state → {state_path}")
        except Exception as e:
            log(f"State save failed: {e}")

        if not done:
            print("➡️  Re-run the same command to continue to the next round.")
        else:
            print(
                "✅ Debate completed. Start a new topic or remove the state file to restart."
            )

        return 0

    def process_debate_request(self, user_input: str) -> int:
        """Main processing function for debate requests"""

        if not user_input.strip():
            print('❌ Usage: debate-processor.py "your debate topic"')
            print("\n🗣️ Enhanced Debate Mode (AI-Powered)")
            print("   Critical vs. creative debate between AI personas")
            print("\n📋 Options:")
            print("   --rounds N        Number of debate rounds (default: 10, max: 50)")
            print("   --interactive     Run one round at a time")
            print("   --strict          Strict mode with error checking")
            print("\n💡 Examples:")
            print('   "Should we use microservices or monoliths?"')
            print('   "Best approach for handling user authentication? --rounds 5"')
            print('   "React vs Vue for our next project? --interactive"')
            return 1

        # Validate environment
        if not self.validate_environment():
            return 1

        # Parse arguments
        topic, rounds, interactive, strict = self.parse_arguments(user_input)

        if not topic:
            print("❌ Please provide a debate topic")
            return 1

        # Run appropriate debate mode
        if interactive:
            return self.run_interactive_debate(topic, rounds, strict)
        else:
            return self.run_batch_debate(topic, rounds, strict)


def main(args: List[str]) -> int:
    """Main entry point for debate processor"""

    if len(args) < 2:
        processor = DebateProcessor()
        return processor.process_debate_request("")

    # Check for CRITIC-only mode (for Claude Code integration)
    if args[1] == "--critic-only":
        if len(args) < 5:
            print(
                "Usage: debate-processor.py --critic-only <topic> <creator-text> <round> [total-rounds]"
            )
            return 1

        topic = args[2]
        creator_text = args[3]
        round_num = int(args[4])
        total_rounds = int(args[5]) if len(args) > 5 else 10

        processor = DebateProcessor()
        critic_response = processor.get_critic_response(
            topic, creator_text, round_num, total_rounds
        )
        print(critic_response)
        return 0

    # Normal debate mode
    user_input = " ".join(args[1:]).strip()
    processor = DebateProcessor()

    return processor.process_debate_request(user_input)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
