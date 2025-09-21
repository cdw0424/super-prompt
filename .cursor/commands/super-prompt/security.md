---
description: security command - Security analysis and threat modeling
run: mcp
server: super-prompt
tool: sp_security
args:
---
  query: "${input}"
## Execution Mode

➡️ Execution: This command executes via MCP (server: super-prompt; tool as defined above).

**Query:** \${input}

### ⚠️ **Analysis Status: Incomplete**

Security execution completed but returned no content. This may indicate:

1. **Query too complex** - Try breaking it into smaller parts
2. **Module import issues** - Check Python path configuration
3. **Function execution error** - Verify security function implementation

### 💡 **Suggestions:**

- Simplify your query and try again
- Check Python environment and dependencies
- Verify the security module is properly installed

**Raw Output:** (empty)\`;
      }

      return result;

    } catch (error) {
      console.error(\`-------- security: Inline execution failed: \${error.message}\`);

      return \`## 🛡️ **Security Analysis Error**

**Query:** \${input}

### ❌ **Execution Failed**

The inline security execution encountered an error:

**Error:** \${error.message}

### 🔧 **Troubleshooting Steps:**

1. **Check Python Installation:**
   \`\`\`bash
   python3 --version
   pip list | grep super-prompt
   \`\`\`

2. **Verify Module Path:**
   \`\`\`bash
   ls -la \${path.join(__dirname, '..', '..', '..', '..', '..', 'packages', 'core-py')}
   \`\`\`

3. **Test Basic Import:**
   \`\`\`bash
   python3 -c "from super_prompt.mcp_server import run_prompt_based_workflow; print('Import successful')"
   \`\`\`

4. **Check Environment:**
   \`\`\`bash
   echo \$PYTHONPATH
   \`\`\`

### 💡 **Alternative:**
You can also try the MCP-based security command if inline execution continues to fail.

**Fallback Command:** \`/super-prompt/security "\${input}"\` (will use MCP server)\`;
    }
  }

  // Export the main function
  module.exports = runSecurityCommand;

# 🛡️ **Security - Analysis & Threat Modeling Specialist**

**Expert Focus**: Security vulnerability assessment and threat modeling

## 🎯 **Security Analysis Workflow**

### **Single Step Analysis:**

1. **🛡️ Security Analysis** - Current Tool (security)
   - Analyze security vulnerabilities and threats
   - Identify potential security risks and attack vectors
   - Provide comprehensive security recommendations and best practices

## 🏗️ **Implementation Strategy**

### **Current Structure vs Optimized Structure:**

| **Current Structure** | **Optimized Structure** |
|----------------------|-------------------------|
| Direct function calls | Single `sp_security` MCP call |
| Complex integrations | Clean MCP protocol compliance |
| Manual analysis | Automated security assessment |

### **Security TODO System:**

## 📋 **Security Analysis TODO List**

### Phase 1: Security Assessment
- [x] **Security Overview**
  - Query: `${input}`
- [x] **Current Security Posture Analysis**
  - Identify existing security measures and controls

### Phase 2: Threat Identification
- [ ] **Vulnerability Assessment**
  - Identify security vulnerabilities and weaknesses
- [ ] **Threat Modeling**
  - Analyze potential attack vectors and threat scenarios

### Phase 3: Risk Analysis
- [ ] **Risk Assessment**
  - Evaluate security risks and potential impacts
- [ ] **Compliance Review**
  - Review security compliance requirements and standards

### Phase 4: Security Recommendations
- [ ] **Security Controls Implementation**
  - Recommend security controls and countermeasures
- [ ] **Security Monitoring Setup**
  - Establish security monitoring and incident response

## 🚀 **Execution Method**

### **Single MCP Execution Mode:**
1. User inputs `/super-prompt/security "security query"`
2. `sp_security` tool executes alone
3. One persona performs complete security analysis
4. Single comprehensive security assessment output

### **Mode-Specific Optimization:**
- **Grok Mode**: Creative security solutions and innovative approaches
- **GPT Mode**: Structured security analysis and proven methodologies

### **Usage Example:**
```
1. /super-prompt/security "Analyze system security vulnerabilities"
    ↓
2. sp_security executes alone (safe single call)
    ↓
3. One persona performs complete security analysis
    ↓
4. Comprehensive security assessment output
```

## 💡 **Security Advantages**

### **1. Single Execution Safety**
- Execute only one MCP tool per security analysis
- Complete prevention of infinite recursion and circular calls

### **2. Comprehensive Analysis**
- System-wide security assessment
- Vulnerability identification and threat modeling
- Risk assessment and compliance review

### **3. Security Best Practices**
- Industry-standard security frameworks and methodologies
- OWASP, NIST, and other security standards compliance
- Defense-in-depth security architecture recommendations

### **4. Implementation Guidance**
- Concrete security control implementation plans
- Incident response and monitoring system setup
- Security awareness and training recommendations

## 🧠 **Strategic Planning Support**

**For complex reasoning and strategic planning tasks**, consider using the high command to get comprehensive analysis and plan development:

```bash
/super-prompt/high "Your strategic planning query here"
```

The high command provides:
- Deep reasoning and problem analysis
- Comprehensive strategic planning
- Implementation roadmap development
- Risk assessment and mitigation strategies

**When to use high command:**
- Complex system design decisions
- Strategic planning and roadmap development
- Architecture analysis and optimization
- Risk assessment and mitigation planning
- Multi-phase implementation strategies

## 🔥 **Conclusion**

Security provides **comprehensive security analysis and threat modeling recommendations**!

- ✅ **Single safe execution** of security analysis
- ✅ **Complete vulnerability assessment** in one call
- ✅ **Industry best practices** for security implementation
- ✅ **Implementation guidance** for security controls

Now **professional security analysis** is available through single MCP execution! 🛡️✨
