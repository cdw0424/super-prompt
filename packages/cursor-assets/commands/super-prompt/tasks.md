---
description: tasks command - SDD Task Breakdown
run: mcp
server: super-prompt
tool: sp_tasks
args:
  query: "${input}"
  persona: "tasks"
## Execution Mode

➡️ Execution: sp_tasks MCP (server: super-prompt; tool as defined above).

---

# 📋 **Tasks - SDD Task Breakdown**

**SDD Phase 3**: Transform implementation plan into actionable tasks

## 🎯 **Task Breakdown Workflow**

### **Complete SDD Workflow:**
```
1. /super-prompt/specify "feature description" ✅ 완료
2. /super-prompt/plan "use spec from above"    ✅ 완료
3. /super-prompt/tasks "use plan from above"  ← 현재 단계
```

### **Single Step Analysis:**

1. **📋 Task Breakdown** - Current Tool (tasks)
   - Transform implementation plan into detailed, actionable tasks
   - Apply optimized task breakdown strategy based on mode (GPT/Grok)
   - Create prioritized task list with dependencies and estimates
   - Generate executable work items for development team

## 🏗️ **SDD Task Structure**

### **Current Structure vs SDD Task Structure:**

| **Current Structure** | **SDD Task Structure** |
|----------------------|-------------------------|
| Basic task list | Comprehensive task breakdown |
| Simple to-do items | Detailed work packages with estimates |
| Manual prioritization | Dependency-based task planning |

## 🚀 **Execution Method**

### **Single MCP Execution Mode:**
1. User inputs `/super-prompt/tasks "break down the OAuth implementation plan"`
2. `sp_tasks` tool executes alone
3. One persona performs all task breakdown work
4. Single comprehensive task breakdown output

### **Mode-Specific Optimization:**
- **Grok Mode**: Creative task organization and innovative breakdown approaches
- **GPT Mode**: Systematic task decomposition and structured planning

### **Usage Example:**
```
/super-prompt/tasks "Break down the OAuth authentication implementation plan"
    ↓
2. sp_tasks executes alone (safe single call)
    ↓
3. One persona performs all task breakdown work
    ↓
4. Comprehensive SDD task breakdown output
```

## 💡 **Innovative Advantages**

### **1. SDD Methodology Integration**
- Completes the SDD workflow (Specify → Plan → Tasks)
- Transforms high-level plans into executable work items
- Ensures complete implementation coverage

### **2. Dependency Management**
- Identify task dependencies and prerequisites
- Create logical task execution order
- Establish critical path and parallel work streams

### **3. Effort Estimation**
- Provide realistic time estimates for each task
- Consider complexity and technical challenges
- Support project planning and resource allocation

## 📋 **Task Breakdown TODO List**

### Phase 1: Task Analysis
- [x] **Task Decomposition**
  - Break down implementation plan into manageable tasks
- [x] **Current Mode Task Strategy**
  - Apply optimized breakdown method based on mode

### Phase 2: Task Organization
- [ ] **Dependency Mapping**
  - Identify task prerequisites and relationships
- [ ] **Priority Assignment**
  - High, medium, low priority classification

### Phase 3: Effort Estimation
- [ ] **Task Complexity Assessment**
  - Evaluate technical challenges and risks
- [ ] **Time Estimation**
  - Realistic effort estimates in hours/days

### Phase 4: Task Documentation
- [ ] **Acceptance Criteria**
  - Define completion requirements for each task
- [ ] **Deliverables**
  - Specify expected outputs and artifacts

### Phase 5: Implementation Roadmap
- [ ] **Sprint Planning**
  - Group tasks into development iterations
- [ ] **Milestone Definition**
  - Establish measurable progress checkpoints

## 🧠 **SDD Workflow Integration**

**Complete SDD workflow achieved!**

```bash
# Phase 1: Requirements
/super-prompt/specify "Define requirements for user authentication"
/super-prompt/plan "Create implementation plan for the auth system"
/super-prompt/tasks "Break down plan into executable tasks" ← 현재 위치
```

**SDD Workflow Benefits:**
- **Specify**: Creates comprehensive requirements foundation
- **Plan**: Develops technical roadmap and architecture
- **Tasks**: Produces actionable development work items

## 📊 **Task Management Features**

### **Task Attributes:**
- **Priority**: Critical, High, Medium, Low
- **Complexity**: Simple, Medium, Complex
- **Dependencies**: Prerequisites and blocking tasks
- **Estimates**: Time and effort requirements
- **Acceptance Criteria**: Completion requirements

### **Organization:**
- **Epics**: Large feature groups
- **Stories**: User-facing functionality
- **Tasks**: Technical implementation items
- **Subtasks**: Detailed implementation steps

## 🔥 **Conclusion**

This completes **Phase 3 of Spec-Driven Development**!

- ✅ **Complete SDD Workflow**: Specify → Plan → Tasks
- ✅ **Actionable Tasks**: Detailed work breakdown with estimates
- ✅ **Dependency Management**: Logical task execution order
- ✅ **Project Execution**: Ready for development team implementation

**SDD Workflow Complete! Ready for Implementation!** 🚀📋✅

---

## 🎯 **SDD Summary**

The complete Spec-Driven Development workflow:

1. **📋 Specify**: Requirements gathering and specification
2. **📋 Plan**: Implementation planning and architecture design
3. **📋 Tasks**: Task breakdown and project execution planning

Each phase builds upon the previous, creating a comprehensive development approach that ensures quality, feasibility, and successful implementation.

- Review the project dossier at `.super-prompt/context/project-dossier.md`; if it is missing, run `/super-prompt/init` to regenerate it.
