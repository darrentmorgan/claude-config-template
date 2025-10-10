#!/bin/bash
# Verify Agent Setup Script
# Tests that plugin agents are properly configured and accessible

set -e

echo "🔍 Verifying Claude Code Agent Setup..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Check 1: Verify no test-automator references
echo "📋 Checking for deprecated test-automator references..."
if grep -r "test-automator" .claude/ --include="*.json" --include="*.ts" --include="*.sh" 2>/dev/null | grep -v "GLOBAL_AGENT_CLEANUP.md" | grep -v "PLUGIN_AGENT_GUIDE.md"; then
    echo -e "${RED}✗ Found test-automator references (should be removed)${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ No deprecated test-automator references${NC}"
fi
echo ""

# Check 2: Verify delegation-map.json exists and has plugin agents
echo "📋 Checking delegation-map.json..."
if [ ! -f ".claude/agents/delegation-map.json" ]; then
    echo -e "${RED}✗ delegation-map.json not found${NC}"
    ERRORS=$((ERRORS + 1))
else
    if grep -q "testing-suite:test-engineer" ".claude/agents/delegation-map.json"; then
        echo -e "${GREEN}✓ Plugin agent 'testing-suite:test-engineer' configured${NC}"
    else
        echo -e "${YELLOW}⚠ Plugin agent 'testing-suite:test-engineer' not found in delegation-map.json${NC}"
    fi
fi
echo ""

# Check 3: Verify GitHub Actions workflows
echo "📋 Checking GitHub Actions workflows..."
if [ -f ".github/workflows/pr-tests.yml" ]; then
    echo -e "${GREEN}✓ PR tests workflow exists${NC}"
else
    echo -e "${RED}✗ PR tests workflow missing${NC}"
    ERRORS=$((ERRORS + 1))
fi

if [ -f ".github/workflows/auto-merge.yml" ]; then
    echo -e "${GREEN}✓ Auto-merge workflow exists${NC}"
else
    echo -e "${RED}✗ Auto-merge workflow missing${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 4: Verify hooks directory
echo "📋 Checking hooks..."
if [ -d ".claude/hooks" ]; then
    HOOK_COUNT=$(find .claude/hooks -name "*.sh" -type f | wc -l | tr -d ' ')
    echo -e "${GREEN}✓ Hooks directory exists (${HOOK_COUNT} hooks found)${NC}"

    if [ -f ".claude/hooks/post-milestone.sh" ]; then
        echo -e "${GREEN}✓ post-milestone.sh hook exists${NC}"
    else
        echo -e "${YELLOW}⚠ post-milestone.sh hook not found${NC}"
    fi
else
    echo -e "${RED}✗ Hooks directory missing${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 5: Verify slash commands
echo "📋 Checking slash commands..."
if [ -d ".claude/commands" ]; then
    CMD_COUNT=$(find .claude/commands -name "*.md" -type f | wc -l | tr -d ' ')
    echo -e "${GREEN}✓ Commands directory exists (${CMD_COUNT} commands found)${NC}"

    if [ -f ".claude/commands/commit-push-pr.md" ]; then
        echo -e "${GREEN}✓ commit-push-pr command exists${NC}"
    else
        echo -e "${YELLOW}⚠ commit-push-pr command not found${NC}"
    fi
else
    echo -e "${RED}✗ Commands directory missing${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 6: Verify sync script
echo "📋 Checking template sync script..."
if [ -f "scripts/sync-from-template.sh" ]; then
    if [ -x "scripts/sync-from-template.sh" ]; then
        echo -e "${GREEN}✓ sync-from-template.sh exists and is executable${NC}"
    else
        echo -e "${YELLOW}⚠ sync-from-template.sh exists but is not executable${NC}"
    fi
else
    echo -e "${RED}✗ sync-from-template.sh missing${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Agent setup is complete.${NC}"
    exit 0
else
    echo -e "${RED}❌ Found ${ERRORS} error(s). Please review the setup.${NC}"
    exit 1
fi
