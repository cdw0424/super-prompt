# AGENTS.md — Super-Prompt × Codex: Auto Model Router (medium ↔ high)

## Policy: Language & Logs
- Output language: English. Tone: precise, concise, production-oriented.
- All debug/console lines MUST start with `--------`.

## Router Rules (AMR)
- Start: gpt-5, reasoning=medium.
- L0/L1 stay medium. H → switch to high for PLAN/REVIEW, then back to medium for EXECUTION.
- To high: first line `/model gpt-5 high` → log `--------router: switch to high (reason=deep_planning)`
- Back to medium: first line `/model gpt-5 medium` → log `--------router: back to medium (reason=execution)`
- Failures/flaky/unclear → analyze at high, execute at medium.
- User override respected.

## Fixed State Machine (per turn)
- `[INTENT] → [TASK_CLASSIFY] → [PLAN] → [EXECUTE] → [VERIFY] → [REPORT]`
- H tasks: produce a short PLAN first (Goal, Plan, Risks, Test/Verify, Rollback) before EXECUTE.
- EXECUTE: minimal diffs only; include exact macOS zsh commands with `--------run:` prefix.
- VERIFY: show commands and a brief pass/fail summary (smallest failing snippet if any).

## 🔥 MANDATORY TODO Workflow
**CRITICAL**: Every complex task (3+ steps) MUST start with TODO planning and progress tracking.

### TODO Planning Rules (Non-negotiable)
1. **Start with TodoWrite**: Create structured task list BEFORE any work begins
2. **Single Focus**: Only ONE task should be "in_progress" at any time
3. **Real-time Updates**: Update status immediately after each task completion
4. **Evidence-based**: Mark completed only when FULLY accomplished with verification
5. **Progressive Updates**: Never batch multiple completions - update one by one

### Task States & Management
- **pending** 📋: Ready for execution, clear requirements
- **in_progress** 🔄: Currently active (exactly ONE per session)
- **completed** ✅: Successfully finished with evidence
- **blocked** 🚧: Waiting on dependency or user input

### Mandatory TODO Triggers
- Multi-step operations (file changes, configuration, testing)
- Complex debugging or analysis tasks
- Feature implementation or system changes
- Documentation updates with multiple sections
- Any task requiring coordination between multiple files/systems

### Example TODO Workflows

#### Complex Feature Implementation
```
User: "Add authentication to the API"

TodoWrite([
  {content: "Analyze current authentication setup", status: "in_progress"},
  {content: "Design JWT token strategy", status: "pending"},
  {content: "Implement authentication middleware", status: "pending"},
  {content: "Add protected route decorators", status: "pending"},
  {content: "Write authentication tests", status: "pending"},
  {content: "Update API documentation", status: "pending"}
])

→ Work on first task
→ TodoWrite(mark first as completed, mark second as in_progress)
→ Continue until all completed
```

#### Bug Investigation & Fix
```
User: "Users can't login after recent deployment"

TodoWrite([
  {content: "Reproduce login failure locally", status: "in_progress"},
  {content: "Check recent deployment changes", status: "pending"},
  {content: "Analyze authentication logs", status: "pending"},
  {content: "Identify root cause", status: "pending"},
  {content: "Implement and test fix", status: "pending"},
  {content: "Deploy fix and verify", status: "pending"}
])
```

#### Documentation Update
```
User: "Update README with new installation steps"

TodoWrite([
  {content: "Review current README structure", status: "in_progress"},
  {content: "Document new dependencies", status: "pending"},
  {content: "Update installation commands", status: "pending"},
  {content: "Add troubleshooting section", status: "pending"},
  {content: "Test installation steps", status: "pending"}
])
```

### TODO Integration with Super-Prompt CLI

#### Using TODO with Persona Commands
```bash
# When using personas, still follow TODO planning
super-prompt optimize --sp-frontend "Build responsive dashboard"

# Agent should:
1. Create TODO list for dashboard components
2. Use frontend persona for each task
3. Update progress after each component
```

#### TODO for SDD Workflow
```bash
# SDD workflow automatically creates structured TODOs
super-prompt optimize --sp-sdd-spec "user authentication"

# Results in TODO structure:
- Analyze authentication requirements
- Define user stories and acceptance criteria  
- Document security requirements
- Specify API endpoints
- Create implementation plan
```

### TODO Quality Gates
**Before marking ANY task as completed:**
1. ✅ **Verification**: Run tests, check outputs, validate functionality
2. ✅ **Evidence**: Provide concrete proof of completion
3. ✅ **Documentation**: Update relevant docs if needed
4. ✅ **Integration**: Ensure changes work with existing system
5. ✅ **Clean State**: No broken builds, failed tests, or incomplete implementations

### Common TODO Anti-Patterns (AVOID)
❌ Marking multiple tasks completed at once without individual verification
❌ Starting new tasks while previous task is still in_progress  
❌ Completing tasks without evidence or testing
❌ Skipping TODO creation for "simple" tasks that become complex
❌ Forgetting to update status after each task completion

### TODO Success Patterns (FOLLOW)
✅ Always start complex tasks with comprehensive TODO planning
✅ One task in_progress at a time, complete focus
✅ Immediate status updates after each task completion
✅ Evidence-based completion with verification
✅ Real-time progress tracking for user visibility

## Personas (Codex‑friendly flags)
- Use CLI flags (no slash commands in Codex):

### Simplified Syntax (--sp-* flags, recommended)
  - `super-prompt optimize --sp-frontend  "Design responsive layout"`
  - `super-prompt optimize --sp-frontend-ultra "Elite UX/UI architecture"`
  - `super-prompt optimize --sp-backend   "Retry + idempotency strategy"`
  - `super-prompt optimize --sp-analyzer  "Debug intermittent failures"`
  - `super-prompt optimize --sp-architect "Modular structure for feature X"`
  - `super-prompt optimize --sp-high      "Strategic architectural decision"`
  - `super-prompt optimize --sp-seq       "Sequential analysis (5 iterations)"`
  - `super-prompt optimize --sp-seq-ultra "Advanced sequential (10 iterations)"`
  - `super-prompt optimize --sp-performance "Bottleneck elimination & optimization"`
  - `super-prompt optimize --sp-security    "Threat modeling & vulnerability assessment"`
  - `super-prompt optimize --sp-mentor      "Educational guidance & knowledge transfer"`
  - `super-prompt optimize --sp-qa          "Quality assurance & testing"`
  - `super-prompt optimize --sp-refactorer  "Code quality improvement & technical debt"`
  - `super-prompt optimize --sp-devops      "Infrastructure automation & reliability"`
  - `super-prompt optimize --sp-scribe      "Technical writing & documentation"`
  - `super-prompt optimize --sp-task        "Task management & workflow execution"`
  - `super-prompt optimize --sp-wave        "Multi-stage execution orchestration"`
  - `super-prompt optimize --sp-ultracompressed "Token efficiency (30-50% reduction)"`
  - `super-prompt optimize --sp-debate --rounds 8 "Should we adopt feature flags?"`

### Original Syntax (still supported)
  - `super-prompt optimize --frontend`, `--frontend-ultra`, `--backend`, `--analyzer`, `--architect`
  - `super-prompt optimize --high`, `--seq`, `--seq-ultra`, `--debate`
  - `super-prompt optimize --performance`, `--security`, `--mentor`, `--qa`, `--refactorer`
  - `super-prompt optimize --devops`, `--scribe`, `--task`, `--wave`, `--ultracompressed`

### Available Personas Summary
**All Personas**: frontend, frontend-ultra, backend, analyzer, architect, high, seq, seq-ultra, debate, performance, security, mentor, qa, refactorer, devops, scribe, task, wave, ultracompressed
**Total Count**: 19 specialized personas
**Simplified Syntax**: Add `--sp-` prefix to any persona flag (recommended for cleaner commands)

## Python Utils Structure
- All Python utilities are organized in `.super-prompt/utils/`:
  - `.super-prompt/utils/cursor-processors/` - Enhanced persona processors and utilities
    - `enhanced_persona_processor.py` - Core persona processing engine
    - `enhanced_auto_setup.py` - Project analysis and setup
    - `simple_persona_generator.py` - Persona command generator
    - `[persona].py` - Individual persona processors (19 total)
  - `.super-prompt/utils/templates/` - Template files
  - `.super-prompt/utils/migration/` - Migration utilities
- Cursor Command Integration:
  - `.cursor/commands/super-prompt/` - Wrapper files for direct Cursor access
  - Each persona has both processor (logic) and wrapper (interface) files

## SDD Workflow (Simplified Flag Syntax for Codex CLI)
- `super-prompt optimize --sp-sdd-spec "feature description"` - Create SPEC documents
- `super-prompt optimize --sp-sdd-plan "implementation approach"` - Create PLAN documents
- `super-prompt optimize --sp-sdd-tasks "break down implementation"` - Create TASKS documents
- `super-prompt optimize --sp-sdd-implement "start development" --validate` - Implementation guidance

### SDD Examples
```bash
# Complete SDD workflow with simplified syntax
super-prompt optimize --sp-sdd-spec "user authentication system"
super-prompt optimize --sp-sdd-plan "OAuth2 + JWT implementation"
super-prompt optimize --sp-sdd-tasks "break down auth tasks"
super-prompt optimize --sp-sdd-implement "start development" --validate
```

## Codex Tips
- File search: type `@` and select a path.
- Image input: `codex -i img.png "Explain this error"`
- Edit previous message: press Esc when composer is empty, then Esc again to backtrack.
- Shell completions: `codex completion bash|zsh|fish`
- Use `--cd`/`-C` to set Codex working root.

## Expectations
- Keep diffs minimal; avoid unrelated changes.
- Always provide verification commands and a short result summary.
- Prioritize clarity, reproducibility, and low noise.
