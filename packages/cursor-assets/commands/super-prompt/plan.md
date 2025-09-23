---
description: plan command - SDD Implementation Planning
run: mcp
server: super-prompt
tool: sp_plan
args:
  query: "${input}"
  persona: "plan"
## Execution Mode

➡️ Execution: sp_plan MCP (server: super-prompt; tool as defined above).

---

# 📋 **Plan - SDD Implementation Planning**

**SDD Phase 2**: Create comprehensive implementation roadmap

## 🎯 **Implementation Planning Workflow**

### **SDD Workflow Integration:**
```
1. /super-prompt/specify "feature description" ✅ 완료
2. /super-prompt/plan "use spec from above"    ← 현재 단계
3. /super-prompt/tasks "use plan from above"
```

### **Single Step Analysis:**

1. **📋 Implementation Planning** - Current Tool (plan)
   - Transform requirements specification into actionable implementation plan
   - Apply optimized planning strategy based on mode (GPT/Grok)
   - Create technical roadmap and architecture decisions
   - Define project phases and milestones

## 🏗️ **SDD Planning Structure**

### **Current Structure vs SDD Planning:**

| **Current Structure** | **SDD Planning Structure** |
|----------------------|---------------------------|
| Basic implementation | Comprehensive technical roadmap |
| Simple task list | Structured implementation phases |
| Manual planning | SDD-driven project planning |

## 🚀 **Execution Method**

### **Single MCP Execution Mode:**
1. User inputs `/super-prompt/plan "implement user auth system"`
2. `sp_plan` tool executes alone
3. One persona performs all planning work
4. Single comprehensive implementation plan output

### **Mode-Specific Optimization:**
- **Grok Mode**: Creative architecture design and innovative approaches
- **GPT Mode**: Systematic project planning and structured execution

### **Usage Example:**
```
/super-prompt/plan "Implement the OAuth authentication system specification"
    ↓
2. sp_plan executes alone (safe single call)
    ↓
3. One persona performs all planning work
    ↓
4. Comprehensive SDD implementation plan output
```

## 💡 **Innovative Advantages**

### **1. SDD Methodology Integration**
- Builds upon specification from Phase 1
- Creates foundation for task breakdown in Phase 3
- Ensures implementation feasibility

### **2. Technical Architecture Planning**
- Define technology stack and architecture patterns
- Establish implementation approach and methodologies
- Plan integration points and dependencies

### **3. Project Timeline Management**
- Create realistic implementation timeline
- Define milestones and deliverables
- Establish risk mitigation strategies

## 📋 **Planning TODO List**

### Phase 1: Technical Analysis
- [x] **Architecture Design**
  - Technology stack selection and justification
- [x] **Current Mode Planning Strategy**
  - Apply optimized planning method based on mode

### Phase 2: Implementation Strategy
- [ ] **Development Approach**
  - Programming languages, frameworks, and tools
- [ ] **Database Design**
  - Data models and storage strategy

### Phase 3: Project Phases
- [ ] **Development Phases**
  - Sprint planning and iteration structure
- [ ] **Integration Strategy**
  - Third-party services and API integrations

### Phase 4: Risk Assessment
- [ ] **Technical Risks**
  - Technology challenges and mitigation
- [ ] **Timeline Risks**
  - Schedule dependencies and buffers

### Phase 5: Success Metrics
- [ ] **Quality Gates**
  - Code review and testing requirements
- [ ] **Performance Benchmarks**
  - Success criteria and KPIs

## 🧠 **SDD Workflow Integration**

**Complete the SDD workflow with:**

```bash
/super-prompt/tasks "Break down the implementation plan above into tasks"
```

The tasks command will:
- Transform implementation plan into detailed tasks
- Assign priorities and dependencies
- Create actionable work items with estimates

**Previous SDD phase:**
```bash
/super-prompt/specify "Define requirements for this feature"
```

The specify command provides:
- Comprehensive requirements specification
- Acceptance criteria and success metrics
- Technical requirements and constraints

## 🔥 **Conclusion**

This is **Phase 2 of Spec-Driven Development**!

- ✅ **Technical Roadmap**: Complete implementation strategy
- ✅ **SDD Integration**: Seamless workflow with specify/tasks
- ✅ **Architecture Planning**: Technology and design decisions
- ✅ **Project Management**: Timeline and risk assessment

**Ready for the final SDD phase: Task Breakdown!** 🚀📋

- Review the project dossier at `.super-prompt/context/project-dossier.md`; if it is missing, run `/super-prompt/init` to regenerate it.
