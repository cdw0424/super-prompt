---
description: db-expert command - Database design and query optimization
run: mcp
server: super-prompt
tool: sp_db_expert
args:
  query: "${input}"
  persona: "db-expert"
## Execution Mode

➡️ Execution: This command executes via MCP (server: super-prompt; tool as defined above).

---

# **db-expert - Super Prompt MCP Tool**

**Expert Focus**: Database architecture, query optimization, and data modeling

## 🎯 **Database Analysis Workflow**

### **Single Step Analysis:**

1. **🗄️ Database Analysis** - Current Tool (db-expert)
   - Analyze database schema, queries, and performance
   - Identify optimization opportunities and design improvements
   - Provide comprehensive database recommendations and best practices

## 🏗️ **Implementation Strategy**

### **Current Structure vs Optimized Structure:**

| **Current Structure** | **Optimized Structure** |
|----------------------|-------------------------|
| Direct function calls | Single `sp_db_expert` MCP call |
| Complex integrations | Clean MCP protocol compliance |
| Manual analysis | Automated database assessment |

### **Database TODO System:**

## 📋 **Database Analysis TODO List**

### Phase 1: Database Assessment
- [x] **Database Overview**
  - Query: `${input}`
- [x] **Current Database Analysis**
  - Identify existing database schema and architecture

### Phase 2: Schema Analysis
- [ ] **Data Model Review**
  - Review database schema and data relationships
- [ ] **Index Optimization**
  - Analyze and optimize database indexes

### Phase 3: Query Optimization
- [ ] **Query Performance Analysis**
  - Identify slow queries and optimization opportunities
- [ ] **Query Refactoring**
  - Refactor queries for better performance

### Phase 4: Database Architecture
- [ ] **Scalability Planning**
  - Plan database scalability and growth strategies
- [ ] **Backup & Recovery Setup**
  - Establish database backup and recovery procedures

## 🚀 **Execution Method**

### **Single MCP Execution Mode:**
1. User inputs `/super-prompt/db-expert "database query"`
2. `sp_db_expert` tool executes alone
3. One persona performs complete database analysis
4. Single comprehensive database assessment output

### **Mode-Specific Optimization:**
- **Grok Mode**: Creative database solutions and innovative approaches
- **GPT Mode**: Structured database design and proven methodologies

### **Usage Example:**
```
1. /super-prompt/db-expert "Optimize database query performance"
    ↓
2. sp_db_expert executes alone (safe single call)
    ↓
3. One persona performs complete database analysis
    ↓
4. Comprehensive database assessment output
```

## 💡 **Database Advantages**

### **1. Single Execution Safety**
- Execute only one MCP tool per database analysis
- Complete prevention of infinite recursion and circular calls

### **2. Comprehensive Analysis**
- Database schema and architecture assessment
- Query performance analysis and optimization
- Index strategy and data modeling review

### **3. Database Best Practices**
- Industry-standard database design patterns
- Normalization, denormalization, and data integrity
- Performance tuning and optimization techniques

### **4. Implementation Guidance**
- Concrete database optimization implementation plans
- Schema refactoring and migration strategies
- Monitoring and maintenance procedure setup

## 🔥 **Conclusion**

DB Expert provides **comprehensive database design and optimization recommendations**!

- ✅ **Single safe execution** of database analysis
- ✅ **Complete schema and query optimization** in one call
- ✅ **Industry best practices** for database design
- ✅ **Implementation guidance** for database optimization

Now **professional database expertise** is available through single MCP execution! 🗄️✨
