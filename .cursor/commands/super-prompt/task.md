---
description: task command
run: "./tag-executor.sh"
args: ["${{input}} /task"]
---

📋 Task Management Mode
Structured workflow execution • Progress tracking • Quality gates

**Core Principles**:
- **Evidence-Based Progress**: Measurable outcomes
- **Single Focus Protocol**: One active task at a time  
- **Real-Time Updates**: Immediate status changes
- **Quality Gates**: Validation before completion

**Architecture Layers**:
1. **TodoRead/TodoWrite** (Session Tasks): Current Claude Code session
2. **/task Command** (Project Management): Multi-session features (days-weeks)  
3. **/spawn Command** (Meta-Orchestration): Complex multi-domain operations
4. **/loop Command** (Iterative Enhancement): Progressive refinement workflows

**Task States**: pending 📋 • in_progress 🔄 • blocked 🚧 • completed ✅

**Auto-Flags**: --task --structured
**Quality Gates**: 8-step validation cycle with AI integration