#!/bin/bash
# Super Prompt - SDD Documentation Update Script
# Updates SDD documents with current project status
# Usage: ./scripts/cursor/update-sdd-docs.sh [project-name]

set -e

PROJECT_NAME="${1:-default}"
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date +%H:%M:%S)

PROJECT_DIR="docs/sdd/projects/$PROJECT_NAME"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Project '$PROJECT_NAME' not found"
    echo "Available projects:"
    ls docs/sdd/projects/ 2>/dev/null || echo "  No projects found"
    echo ""
    echo "Create a new project with:"
    echo "  ./scripts/cursor/create-sdd-project.sh \"Project Name\""
    exit 1
fi

echo "📚 Updating SDD documentation for project: $PROJECT_NAME"
echo "📅 Date: $CURRENT_DATE $CURRENT_TIME"
echo ""

# Update project dossier if it exists
DOSSIER_FILE=".super-prompt/context/project-dossier.md"
if [ -f "$DOSSIER_FILE" ]; then
    echo "📋 Updating project dossier..."
    # Add current date/time to dossier
    echo "" >> "$DOSSIER_FILE"
    echo "## Last SDD Update: $CURRENT_DATE $CURRENT_TIME" >> "$DOSSIER_FILE"
    echo "- Updated SDD documentation for project: $PROJECT_NAME" >> "$DOSSIER_FILE"
    echo "✓ Project dossier updated"
else
    echo "⚠️  Project dossier not found at $DOSSIER_FILE"
fi

# Check and update specification document
SPEC_FILE="$PROJECT_DIR/01-specification/spec.md"
if [ -f "$SPEC_FILE" ]; then
    echo "📝 Checking specification document..."
    # Update last modified date
    sed -i.bak "s/**Last Updated**: .*/**Last Updated**: $CURRENT_DATE/g" "$SPEC_FILE" && rm "$SPEC_FILE.bak"
    echo "✓ Specification document updated"
else
    echo "⚠️  Specification document not found: $SPEC_FILE"
fi

# Check and update planning document
PLAN_FILE="$PROJECT_DIR/02-planning/plan.md"
if [ -f "$PLAN_FILE" ]; then
    echo "📝 Checking planning document..."
    # Update last modified date
    sed -i.bak "s/**Last Updated**: .*/**Last Updated**: $CURRENT_DATE/g" "$PLAN_FILE" && rm "$PLAN_FILE.bak"
    echo "✓ Planning document updated"
else
    echo "⚠️  Planning document not found: $PLAN_FILE"
fi

# Check and update tasks document
TASKS_FILE="$PROJECT_DIR/03-tasks/tasks.md"
if [ -f "$TASKS_FILE" ]; then
    echo "📝 Checking tasks document..."
    # Update last modified date
    sed -i.bak "s/**Last Updated**: .*/**Last Updated**: $CURRENT_DATE/g" "$TASKS_FILE" && rm "$TASKS_FILE.bak"
    echo "✓ Tasks document updated"
else
    echo "⚠️  Tasks document not found: $TASKS_FILE"
fi

# Check and update implementation document
IMPL_FILE="$PROJECT_DIR/04-implementation/implementation.md"
if [ -f "$IMPL_FILE" ]; then
    echo "📝 Checking implementation document..."
    # Update last modified date
    sed -i.bak "s/**Last Updated**: .*/**Last Updated**: $CURRENT_DATE/g" "$IMPL_FILE" && rm "$IMPL_FILE.bak"
    echo "✓ Implementation document updated"
else
    echo "⚠️  Implementation document not found: $IMPL_FILE"
fi

# Generate status summary
echo ""
echo "📊 SDD Documentation Status Summary:"
echo "==================================="

echo ""
echo "📁 Project Structure:"
ls -la "$PROJECT_DIR"

echo ""
echo "📋 Document Status:"
echo "  • Specification: $([ -f "$SPEC_FILE" ] && echo "✓ Present" || echo "✗ Missing")"
echo "  • Planning: $([ -f "$PLAN_FILE" ] && echo "✓ Present" || echo "✗ Missing")"
echo "  • Tasks: $([ -f "$TASKS_FILE" ] && echo "✓ Present" || echo "✗ Missing")"
echo "  • Implementation: $([ -f "$IMPL_FILE" ] && echo "✓ Present" || echo "✗ Missing")"

echo ""
echo "🎯 Next Steps:"
echo "1. Use /super-prompt/specify to update requirements"
echo "2. Use /super-prompt/plan to update implementation approach"
echo "3. Use /super-prompt/tasks to track progress"
echo "4. Use /super-prompt/implement to document changes"
echo ""
echo "📂 Project location: $PROJECT_DIR"
echo "🔍 View project: ls $PROJECT_DIR"
echo ""
echo "✅ SDD documentation update complete!"
