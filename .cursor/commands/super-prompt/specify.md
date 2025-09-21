---
description: specify command - SDD Requirements Specification
run: mcp
server: super-prompt
tool: sp_specify
args:
  query: "${input}"
  persona: "specify"
## Execution Mode

➡️ Execution: This command executes via MCP (server: super-prompt; tool as defined above).

---

# 📋 **Specify - SDD Requirements Specification**

**SDD Phase 1**: Create comprehensive feature specifications

## 🎯 **Requirements Specification Workflow**

### **Single Step Analysis:**

1. **📋 Requirements Gathering** - Current Tool (specify)
   - Apply SDD methodology for systematic requirements specification
   - Use optimized analysis strategy based on mode (GPT/Grok)
   - Identify functional and non-functional requirements
   - Create comprehensive specification document

## 🏗️ **SDD Integration**

### **SDD Workflow:**
```
1. /super-prompt/specify "feature description"  ← 현재 단계
2. /super-prompt/plan "use spec from above"
3. /super-prompt/tasks "use plan from above"
```

### **Current Structure vs SDD Structure:**

| **Current Structure** | **SDD Structure** |
|----------------------|-------------------|
| Basic requirements | Comprehensive SDD spec |
| Simple documentation | Structured specification |
| Manual process | SDD methodology |

## 🚀 **Execution Method**

### **Single MCP Execution Mode:**
1. User inputs `/super-prompt/specify "new feature requirements"`
2. `sp_specify` tool executes alone
3. One persona performs all specification work
4. Single comprehensive specification output

### **Mode-Specific Optimization:**
- **Grok Mode**: Creative requirements discovery and innovative solutions
- **GPT Mode**: Structured requirements analysis and systematic documentation

### **Usage Example:**
```
/super-prompt/specify "Implement user authentication system with OAuth"
    ↓
2. sp_specify executes alone (safe single call)
    ↓
3. One persona performs all specification work
    ↓
4. Comprehensive SDD specification output
```

## 💡 **Innovative Advantages**

### **1. SDD Methodology Integration**
- Follows Spec-Driven Development principles
- Creates foundation for plan and tasks phases
- Ensures comprehensive requirements coverage

### **2. Mode-Specific Optimization**
- Auto-optimize specification method based on Grok/GPT mode
- Perform single specification leveraging each mode's strengths

### **3. Systematic Documentation**
- Generate complete requirement specifications
- Include acceptance criteria and success metrics
- Provide implementation guidance

## 📋 **Specification TODO List**

### Phase 1: Requirements Analysis
- [x] **Feature Description & Scope**
  - Query: `${input}`
- [x] **Current Mode Specification Strategy**
  - Apply optimized specification method based on mode

### Phase 2: Functional Requirements
- [ ] **Core Functionality Definition**
  - Primary use cases and user stories
- [ ] **User Interface Requirements**
  - UI/UX specifications and wireframes

### Phase 3: Non-Functional Requirements
- [ ] **Performance Requirements**
  - Response times, throughput, scalability
- [ ] **Security Requirements**
  - Authentication, authorization, data protection

### Phase 4: Technical Specifications
- [ ] **Architecture Considerations**
  - Technology stack and integration points
- [ ] **Data Requirements**
  - Database schema and data flow

### Phase 5: Acceptance Criteria
- [ ] **Success Metrics**
  - Measurable acceptance criteria
- [ ] **Testing Strategy**
  - Test cases and validation methods

## 🧠 **SDD Workflow Integration**

**For complete SDD workflow, continue with:**

```bash
/super-prompt/plan "Implement the specification above"
/super-prompt/tasks "Use the plan above for task breakdown"
```

The plan command will:
- Create implementation roadmap based on specification
- Define technical approach and architecture decisions
- Establish project timeline and milestones

The tasks command will:
- Break down implementation into manageable tasks
- Assign priorities and dependencies
- Create detailed task specifications

## 🔥 **Conclusion**

This is the **foundation of Spec-Driven Development**!

- ✅ **Comprehensive Requirements**: Complete specification coverage
- ✅ **SDD Integration**: Seamless workflow with plan/tasks
- ✅ **Mode Optimization**: GPT/Grok specific approaches
- ✅ **Systematic Documentation**: Professional specification output

**Ready for the next SDD phase: Planning!** 🚀📋
