#!/bin/bash
# Sync Claude Config from Template Repository
# Pulls latest changes from claude-config-template and applies to current project

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔄 Syncing Claude Config from Template...${NC}\n"

# Configuration
TEMPLATE_REPO="https://github.com/darrentmorgan/claude-config-template.git"
TEMPLATE_BRANCH="main"
TEMP_DIR="/tmp/claude-config-template-$$"

# Get current directory
PROJECT_DIR=$(pwd)

echo -e "${BLUE}📍 Current project: ${PROJECT_DIR}${NC}"
echo -e "${BLUE}📦 Template repo: ${TEMPLATE_REPO}${NC}\n"

# Step 1: Clone template repository
echo -e "${BLUE}1️⃣  Cloning template repository...${NC}"
git clone --depth 1 --branch "$TEMPLATE_BRANCH" "$TEMPLATE_REPO" "$TEMP_DIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to clone template repository${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Template cloned${NC}\n"

# Step 2: Backup existing .claude directory
echo -e "${BLUE}2️⃣  Backing up existing .claude directory...${NC}"
BACKUP_DIR=".claude-backup-$(date +%Y%m%d-%H%M%S)"

if [ -d ".claude" ]; then
    cp -r .claude "$BACKUP_DIR"
    echo -e "${GREEN}✓ Backup created: ${BACKUP_DIR}${NC}\n"
else
    echo -e "${YELLOW}⚠ No existing .claude directory found${NC}\n"
fi

# Step 3: Copy template files (preserve project-specific configs)
echo -e "${BLUE}3️⃣  Syncing template files...${NC}"

# Files to sync (overwrite)
SYNC_FILES=(
    ".claude/agents/delegation-map.json"
    ".claude/agents/mcp-mapping.json"
    ".claude/hooks"
    ".claude/scripts"
    ".github/workflows"
    "commands"
    "docs"
)

# Files to preserve (don't overwrite if they exist)
PRESERVE_FILES=(
    ".claude/settings.local.json"
    ".claude/.env"
)

mkdir -p .claude/agents
mkdir -p .claude/hooks
mkdir -p .claude/scripts
mkdir -p .github/workflows
mkdir -p commands
mkdir -p docs

# Sync files
for file in "${SYNC_FILES[@]}"; do
    if [ -e "$TEMP_DIR/$file" ]; then
        echo -e "  ${GREEN}↓${NC} Syncing: $file"

        if [ -d "$TEMP_DIR/$file" ]; then
            # Directory - sync recursively
            rsync -a --delete "$TEMP_DIR/$file/" "./$file/"
        else
            # File - copy directly
            cp "$TEMP_DIR/$file" "./$file"
        fi
    fi
done

echo -e "${GREEN}✓ Template files synced${NC}\n"

# Step 4: Preserve project-specific files
echo -e "${BLUE}4️⃣  Preserving project-specific configurations...${NC}"

for file in "${PRESERVE_FILES[@]}"; do
    if [ -e "$BACKUP_DIR/$file" ] && [ ! -e "./$file" ]; then
        echo -e "  ${YELLOW}↩${NC}  Restoring: $file"
        cp "$BACKUP_DIR/$file" "./$file"
    fi
done

echo -e "${GREEN}✓ Project configs preserved${NC}\n"

# Step 5: Check for test-automator references
echo -e "${BLUE}5️⃣  Checking for test-automator references...${NC}"

if grep -r "test-automator" .claude/ --include="*.json" --include="*.ts" --include="*.sh" 2>/dev/null | grep -v "testing-suite:test-engineer" | head -5; then
    echo -e "${YELLOW}⚠ Found test-automator references (see above)${NC}"
    echo -e "${YELLOW}  These should be updated to: testing-suite:test-engineer${NC}\n"
else
    echo -e "${GREEN}✓ No test-automator references found${NC}\n"
fi

# Step 6: Cleanup
echo -e "${BLUE}6️⃣  Cleaning up...${NC}"
rm -rf "$TEMP_DIR"
echo -e "${GREEN}✓ Cleanup complete${NC}\n"

# Summary
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Template Sync Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${BLUE}What was synced:${NC}"
echo -e "  ✓ Agent configurations (delegation-map, mcp-mapping)"
echo -e "  ✓ Hooks (pre-commit, post-milestone, etc.)"
echo -e "  ✓ Scripts (delegation-router, etc.)"
echo -e "  ✓ GitHub Actions workflows"
echo -e "  ✓ Commands (/commit-push-pr, etc.)"
echo -e "  ✓ Documentation"

echo -e "\n${BLUE}Preserved:${NC}"
echo -e "  ✓ .claude/settings.local.json"
echo -e "  ✓ .claude/.env (if exists)"

echo -e "\n${BLUE}Backup location:${NC}"
echo -e "  📁 ${BACKUP_DIR}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Review changes: git status"
echo -e "  2. Test configuration: Run a simple task"
echo -e "  3. Commit if satisfied: git add .claude && git commit"
echo -e "  4. Delete backup if satisfied: rm -rf ${BACKUP_DIR}"

exit 0
