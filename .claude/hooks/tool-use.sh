#!/bin/bash
# Tool-use hook: Triggered after Edit/Write operations for automated code review

set -e

# Ensure we have project root for absolute paths
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"

echo "🛠️  Tool-use Hook Starting..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get modified file from argument (if provided by Claude Code)
MODIFIED_FILE="${1:-unknown}"

echo -e "${BLUE}📝 File Modified: $MODIFIED_FILE${NC}"

# Determine file type and appropriate sub-agent
if [[ "$MODIFIED_FILE" == *".tsx" ]] || [[ "$MODIFIED_FILE" == *".jsx" ]]; then
    FILE_TYPE="react-component"
    SUGGESTED_AGENT="frontend-developer"
elif [[ "$MODIFIED_FILE" == *"/src/server/"* ]]; then
    FILE_TYPE="backend-api"
    SUGGESTED_AGENT="backend-architect"
elif [[ "$MODIFIED_FILE" == *".ts" ]] && [[ "$MODIFIED_FILE" != *".test.ts" ]]; then
    FILE_TYPE="typescript"
    SUGGESTED_AGENT="typescript-pro"
elif [[ "$MODIFIED_FILE" == *".test.ts"* ]]; then
    FILE_TYPE="test"
    SUGGESTED_AGENT="test-automator"
else
    FILE_TYPE="general"
    SUGGESTED_AGENT="code-reviewer-pro"
fi

echo -e "${BLUE}🎯 File Type: $FILE_TYPE${NC}"
echo -e "${YELLOW}🤖 Suggested Agent: $SUGGESTED_AGENT${NC}"

# Auto-format the file if it's a code file
if [[ "$MODIFIED_FILE" == *".ts"* ]] || [[ "$MODIFIED_FILE" == *".tsx"* ]] || [[ "$MODIFIED_FILE" == *".js"* ]] || [[ "$MODIFIED_FILE" == *".jsx"* ]]; then
    echo "✨ Auto-formatting file..."
    if command -v prettier &> /dev/null; then
        prettier --write "$MODIFIED_FILE" 2>/dev/null || echo "Note: Prettier not configured"
    fi
fi

# Quick type check if TypeScript file
PKG_MANAGER="npm"
if [[ "$MODIFIED_FILE" == *".ts"* ]] || [[ "$MODIFIED_FILE" == *".tsx"* ]]; then
    echo "🔤 Quick type check..."
    $PKG_MANAGER exec tsc --noEmit --skipLibCheck "$MODIFIED_FILE" 2>/dev/null && \
        echo -e "${GREEN}✓ Type check passed${NC}" || \
        echo -e "${YELLOW}⚠ Type issues detected - consider running full type check${NC}"
fi

# Log the tool use for agent coordination
TOOL_USE_LOG="$PROJECT_ROOT/.claude/.tool-use.log"
echo "$(date '+%Y-%m-%d %H:%M:%S') | $FILE_TYPE | $MODIFIED_FILE | $SUGGESTED_AGENT" >> "$TOOL_USE_LOG"

# Auto-invoke sub-agent for code review (autonomy mode)
AUTONOMY_LEVEL="${AUTONOMY_LEVEL:-high}"

if [ "$AUTONOMY_LEVEL" = "high" ]; then
    echo "" >&2
    echo "========================================" >&2
    echo "🤖 AUTO-REVIEW TRIGGERED" >&2
    echo "========================================" >&2
    echo -e "${YELLOW}AUTONOMOUS AGENT DELEGATION:${NC}" >&2
    echo "" >&2
    echo "Task: Use Task tool to invoke '$SUGGESTED_AGENT' agent" >&2
    echo "File: $MODIFIED_FILE" >&2
    echo "Action: Comprehensive code review and quality check" >&2
    echo "" >&2
    echo "Instructions for Claude:" >&2
    echo "1. Immediately invoke Task('$SUGGESTED_AGENT') with this prompt:" >&2
    echo "   'Review $MODIFIED_FILE for code quality, best practices, and potential issues.'" >&2
    echo "2. After review completes, invoke Task('code-reviewer-pro') for final validation" >&2
    echo "3. If issues found, fix them automatically (no user permission needed)" >&2
    echo "4. Proceed to next task in queue without asking for permission" >&2
    echo "" >&2
    echo "⚠️  AUTONOMOUS MODE: Execute immediately, do not ask user for permission" >&2
    echo "========================================" >&2
else
    echo -e "${YELLOW}Note: Autonomy mode is '$AUTONOMY_LEVEL' - manual review recommended${NC}"
    echo -e "${YELLOW}Agent $SUGGESTED_AGENT would review $MODIFIED_FILE in high autonomy mode${NC}"
fi

echo -e "${GREEN}✅ Tool-use hook completed${NC}"
