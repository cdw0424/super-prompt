#!/bin/bash
# Super Prompt - MCP-First Code Review Script
# Uses SDD workflow: specify → plan → review → validate
# Usage: ./scripts/cursor/review-changes.sh

set -e

echo "🔍 Super Prompt MCP-First Code Review..."
echo "🤖 Using sp_review, sp_qa, sp_security MCP tools"
echo ""

# Check if cursor-agent is available
if ! command -v cursor-agent &> /dev/null; then
    echo "❌ cursor-agent not found. Install with:"
    echo "   curl https://cursor.com/install -fsS | bash"
    exit 1
fi

echo "📋 Step 1: Evidence-based analysis with sp_analyzer..."
cursor-agent -p --output-format text \
  "/super-prompt/analyzer 'Analyze recent changes for correctness, security, and testing requirements. Provide evidence-based assessment with citations.'"

echo ""
echo "🔍 Step 2: Quality assurance with sp_qa..."
cursor-agent -p --output-format text \
  "/super-prompt/qa 'Review recent changes against testing standards and quality gates. Identify gaps and recommendations.'"

echo ""
echo "🛡️ Step 3: Security assessment with sp_security..."
cursor-agent -p --output-format text \
  "/super-prompt/security 'Security review of recent changes. Check for vulnerabilities, auth issues, and compliance requirements.'"

echo ""
echo "✅ Step 4: Final validation with sp_double_check..."
cursor-agent -p --output-format text \
  "/super-prompt/double-check 'Final validation of review findings. Confirm all risks identified and recommendations provided.'"

echo ""
echo "🎯 Super Prompt review complete!"
echo "📊 Used: sp_analyzer, sp_qa, sp_security, sp_double_check"
echo "🔄 SDD Workflow: Analysis → Quality → Security → Validation"
