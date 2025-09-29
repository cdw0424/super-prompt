#!/bin/bash
# Super Prompt - SDD Project Creation Script
# Creates a new SDD project with proper documentation structure
# Usage: ./scripts/cursor/create-sdd-project.sh "Project Name"

set -e

PROJECT_NAME="$1"
CURRENT_DATE=$(date +%Y-%m-%d)

if [ -z "$PROJECT_NAME" ]; then
    echo "❌ Error: Project name is required"
    echo "Usage: $0 \"Project Name\""
    exit 1
fi

echo "📋 Creating SDD project: $PROJECT_NAME"
echo "📅 Date: $CURRENT_DATE"
echo ""

# Create project directory structure
PROJECT_DIR="docs/sdd/projects/$PROJECT_NAME"
SPEC_DIR="$PROJECT_DIR/01-specification"
PLAN_DIR="$PROJECT_DIR/02-planning"
TASKS_DIR="$PROJECT_DIR/03-tasks"
IMPL_DIR="$PROJECT_DIR/04-implementation"

echo "📁 Creating directory structure..."
mkdir -p "$SPEC_DIR" "$PLAN_DIR" "$TASKS_DIR" "$IMPL_DIR"

# Generate specification document
echo "📝 Generating specification document..."
SPEC_TEMPLATE="docs/sdd/templates/specification-template.md"
SPEC_FILE="$SPEC_DIR/spec.md"

if [ -f "$SPEC_TEMPLATE" ]; then
    sed -e "s/{project-name}/$PROJECT_NAME/g" \
        -e "s/\`date\`/$CURRENT_DATE/g" \
        "$SPEC_TEMPLATE" > "$SPEC_FILE"
    echo "✓ Created: $SPEC_FILE"
else
    echo "⚠️  Specification template not found, creating basic spec.md"
    cat > "$SPEC_FILE" << EOF
# 📋 Project Specification: $PROJECT_NAME

**Created**: $CURRENT_DATE
**Status**: Draft

## Overview
[Project description goes here]

## Requirements
[Requirements go here]

## Next Steps
1. Complete this specification
2. Generate implementation plan
3. Create task breakdown
EOF
fi

# Generate planning document
echo "📝 Generating planning document..."
PLAN_TEMPLATE="docs/sdd/templates/planning-template.md"
PLAN_FILE="$PLAN_DIR/plan.md"

if [ -f "$PLAN_TEMPLATE" ]; then
    sed -e "s/{project-name}/$PROJECT_NAME/g" \
        -e "s/\`date\`/$CURRENT_DATE/g" \
        "$PLAN_TEMPLATE" > "$PLAN_FILE"
    echo "✓ Created: $PLAN_FILE"
else
    echo "⚠️  Planning template not found, creating basic plan.md"
    cat > "$PLAN_FILE" << EOF
# 📝 Implementation Plan: $PROJECT_NAME

**Created**: $CURRENT_DATE
**Status**: Draft

## Implementation Strategy
[Implementation approach goes here]

## Architecture
[Architecture decisions go here]

## Timeline
[Timeline and milestones go here]
EOF
fi

# Generate tasks document
echo "📝 Generating tasks document..."
TASKS_TEMPLATE="docs/sdd/templates/tasks-template.md"
TASKS_FILE="$TASKS_DIR/tasks.md"

if [ -f "$TASKS_TEMPLATE" ]; then
    sed -e "s/{project-name}/$PROJECT_NAME/g" \
        -e "s/\`date\`/$CURRENT_DATE/g" \
        "$TASKS_TEMPLATE" > "$TASKS_FILE"
    echo "✓ Created: $TASKS_FILE"
else
    echo "⚠️  Tasks template not found, creating basic tasks.md"
    cat > "$TASKS_FILE" << EOF
# ✅ Task Breakdown: $PROJECT_NAME

**Created**: $CURRENT_DATE
**Status**: Draft

## Task Overview
[Task breakdown goes here]

## Task List
[Specific tasks go here]

## Progress Tracking
[Progress tracking goes here]
EOF
fi

# Generate implementation document
echo "📝 Generating implementation document..."
IMPL_TEMPLATE="docs/sdd/templates/implementation-template.md"
IMPL_FILE="$IMPL_DIR/implementation.md"

if [ -f "$IMPL_TEMPLATE" ]; then
    sed -e "s/{project-name}/$PROJECT_NAME/g" \
        -e "s/\`date\`/$CURRENT_DATE/g" \
        "$IMPL_TEMPLATE" > "$IMPL_FILE"
    echo "✓ Created: $IMPL_FILE"
else
    echo "⚠️  Implementation template not found, creating basic implementation.md"
    cat > "$IMPL_FILE" << EOF
# 🚀 Implementation: $PROJECT_NAME

**Created**: $CURRENT_DATE
**Status**: Not Started

## Implementation Overview
[Implementation tracking goes here]

## Changes
[Code and configuration changes go here]

## Progress
[Implementation progress goes here]
EOF
fi

# Create project index
PROJECT_INDEX="$PROJECT_DIR/README.md"
cat > "$PROJECT_INDEX" << EOF
# 📋 SDD Project: $PROJECT_NAME

**Created**: $CURRENT_DATE
**Status**: Active

## 📚 Documentation Structure

### Phase 1: Specification
- 📄 [Specification Document](./01-specification/spec.md) - Requirements and scope
- 📄 [Requirements](./01-specification/requirements.md) - Detailed requirements
- 📄 [Context](./01-specification/context.md) - Project context and background

### Phase 2: Planning
- 📄 [Implementation Plan](./02-planning/plan.md) - Architecture and approach
- 📄 [Architecture](./02-planning/architecture.md) - System architecture
- 📄 [Risks](./02-planning/risks.md) - Risk assessment and mitigation

### Phase 3: Tasks
- 📄 [Task Breakdown](./03-tasks/tasks.md) - Detailed task list
- 📄 [Timeline](./03-tasks/timeline.md) - Project timeline
- 📄 [Assignments](./03-tasks/assignments.md) - Task assignments

### Phase 4: Implementation
- 📄 [Implementation](./04-implementation/implementation.md) - Implementation tracking
- 📄 [Changes](./04-implementation/changes.md) - Code and config changes
- 📄 [Results](./04-implementation/results.md) - Implementation results

## 🚀 SDD Workflow

1. **Specify** → Complete specification document
2. **Plan** → Create implementation plan
3. **Tasks** → Break down into specific tasks
4. **Implement** → Execute and track implementation

## 📊 Quick Access

- **View all projects**: ls ../
- **Edit specification**: $SPEC_FILE
- **Edit plan**: $PLAN_FILE
- **Edit tasks**: $TASKS_FILE
- **Edit implementation**: $IMPL_FILE

---

*This project follows the Super Prompt SDD (Scope → Design → Delivery) workflow with comprehensive documentation at every phase.*
EOF

echo ""
echo "✅ SDD Project created successfully!"
echo "📂 Project location: $PROJECT_DIR"
echo ""
echo "📋 Next steps:"
echo "1. Edit $SPEC_FILE to define your requirements"
echo "2. Use /super-prompt/specify to start SDD workflow"
echo "3. Follow SDD phases: plan → tasks → implement"
echo ""
echo "🔍 View project: ls $PROJECT_DIR"
echo "📝 Edit spec: code $SPEC_FILE"
