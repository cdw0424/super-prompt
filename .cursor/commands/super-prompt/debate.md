---
description: debate command
run: "./tag-executor.py"
args: ["${input} /debate"]
---

# 🗣️ Enhanced Debate Mode (AI-Powered)

Focus: Critical vs. creative debate between two AI personas to converge on the best solution through structured dialogue.

Options:
- `--rounds N` (default 10, max 50)

## Roles
- **CRITIC‑AI**: Logic-first critique (find flaws, propose validations, evidence-based analysis)
- **CREATOR‑AI**: Constructive synthesis (improve ideas, propose actionable steps, creative solutions)

## Protocol (configurable rounds)
1) **Problem Framing**: Shared understanding of topic and goals
2) **Alternating Turns**: CRITIC‑AI → CREATOR‑AI (repeat for 10 rounds)
3) **Real Dialogue Flow**:
   - **CRITIC‑AI** analyzes CREATOR‑AI's previous response and provides specific critique
   - **CREATOR‑AI** addresses CRITIC‑AI's specific points and refines the approach
   - Each response builds on the actual content of the previous response
4) **Structured Format**: Each turn includes:
   - **Claims** with evidence/citations
   - **Risks/Assumptions** callouts
   - **Concrete next steps** with expected outcomes
5) **Checkpoints**: Every 3 turns evaluate progress vs acceptance criteria
6) **Termination**: When consensus reached or no new value emerges

## Enhanced Features
- **Real AI Dialogue**: Cursor and Codex actually analyze each other's responses
- **Dynamic Response Generation**: Each AI adapts based on the other's specific feedback
- **Intelligent Critique Analysis**: Responses are tailored to address exact points raised
- **Contextual Evolution**: Solutions improve through iterative, responsive dialogue
- **Automatic Role Switching**: AI seamlessly switches between CRITIC and CREATOR roles
- **Context Preservation**: Full conversation history maintained across turns
- **Structured Output**: Consistent formatting for each debate turn
- **Progress Tracking**: Built-in checkpoint system
- **Final Synthesis**: Comprehensive solution summary

## Evidence and Logging
- Cite sources: code paths + line ranges, or URLs
- '-----' prefix for any runtime/debug logs; never include secrets/PII
- Full debate transcript preserved

## Synthesis (Final Output)
- **Agreed Solution Outline**: Consensus position
- **Stepwise Action Plan**: Small, verifiable steps
- **Risk Assessment**: Open risks with mitigation strategies
- **Validation Framework**: Checklist and ownership assignments

## Debate Flow Template
```
FRAMING
- Topic, goals, constraints, acceptance criteria

TURN 1 — CRITIC‑AI
- Claims + Evidence
- Risks/Assumptions
- Validation Proposals

TURN 1 — CREATOR‑AI
- Improvements/Refinements
- Small Actionable Steps
- Expected Outcomes

[... rounds 2-9 continue alternating ...]

TURN 10 — CRITIC‑AI
- Final Claims + Evidence
- Remaining Risks
- Ultimate Validation

TURN 10 — CREATOR‑AI
- Final Synthesis
- Complete Action Plan
- Success Metrics

FINAL SYNTHESIS
- Consensus Solution
- Implementation Roadmap
- Risk Mitigation Plan
- Validation Framework
```

## Usage Examples

```bash
# Basic debate (10 rounds at once)
./tag-executor.py "Should we use microservices or monoliths? /debate"

# Interactive debate (one round at a time - conversational)
./tag-executor.py "Should we use microservices or monoliths? /debate --interactive"
./tag-executor.py "딱복숭아 vs 물복숭아, 무엇이 더 맛있는가? /debate --interactive --rounds 5"

# Complex topic
./tag-executor.py "AI alignment challenges in autonomous systems /debate"

# Creative debate
./tag-executor.py "The future of human-AI collaboration /debate-interactive"
```

## Real Dialogue Example

**Round 1 - CRITIC‑AI:**
```
Analyzes Cursor's initial response about microservices...
- Identifies specific assumptions about scalability
- Points out missing cost-benefit analysis
- Questions team expertise requirements
```

**Round 1 - CREATOR‑AI:**
```
Addresses each specific critique point...
- Provides detailed cost-benefit metrics
- Includes team capability assessment
- Refines scalability assumptions
```

**This continues for 10 rounds with each AI adapting to the other's specific feedback**

## Interactive Mode Features

### 🎯 **Conversational Debate Flow**
The `/debate-interactive` mode runs debates **one round at a time**, allowing for:

- **Real-time feedback** and course correction
- **Human intervention** at any point
- **Step-by-step analysis** of each debate turn
- **State persistence** between sessions

### 📁 **State Management**
- **Auto-saves** debate state to JSON file
- **Resume capability** - continue from any round
- **Modification support** - edit debate state file directly
- **Clean completion** - auto-deletes state file when finished

### 🔄 **Interactive Workflow**
```
1. Start: ./tag-executor.py "topic /debate-interactive"
2. Review: Read CRITIC-AI and CREATOR-AI responses
3. Decide: Continue, modify, or stop
4. Repeat: Run command again for next round
5. Complete: Automatic final synthesis at round 10
```

### 💡 **When to Use Interactive Mode**
- **Complex topics** requiring human oversight
- **Stakeholder involvement** in the debate process
- **Quality control** at each debate stage
- **Educational purposes** - learn from step-by-step analysis

### 🎮 **Control Options**
- **Continue**: Run command again for next round
- **Modify**: Edit the `debate_state_*.json` file
- **Stop**: Delete the state file
- **Restart**: Use different topic

Note: Fully automated AI debate system - no external CLI dependencies required.
