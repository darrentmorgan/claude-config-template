#!/bin/bash
# Post-Milestone Hook
# Runs after completing major work phases to commit, push, create PR, document changes, and prepare for next phase
#
# Triggers:
# - Manually: .claude/hooks/post-milestone.sh
# - Auto: When milestone completion detected
#
# Actions:
# 1. Run /commit-push-pr command
# 2. Document all changes
# 3. Archive artifacts
# 4. Clear context for next phase
# 5. Update scratch pads and work logs

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
ARTIFACTS_DIR=".claude/artifacts"
ARCHIVE_DIR=".claude/.archive"
WORK_LOG=".claude/.work-log.md"
SCRATCHPAD=".claude/.scratchpad.md"
TIMESTAMP=$(date +"%Y-%m-%d-%H-%M")

echo -e "${BLUE}🏁 Post-Milestone Hook Starting...${NC}" >&2

# Step 1: Check if there are changes to commit
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}⚠ No changes to commit. Skipping milestone completion.${NC}" >&2
    exit 0
fi

# Step 2: Generate commit message from changes
echo -e "${BLUE}📝 Analyzing changes for commit message...${NC}" >&2

# Get list of changed files
CHANGED_FILES=$(git diff --name-only HEAD)
STAGED_FILES=$(git diff --cached --name-only)
ALL_FILES="${CHANGED_FILES}\n${STAGED_FILES}"

# Detect change type
if echo "$ALL_FILES" | grep -q "\.test\.\|\.spec\."; then
    CHANGE_TYPE="test"
    SCOPE="tests"
elif echo "$ALL_FILES" | grep -q "\.md$"; then
    CHANGE_TYPE="docs"
    SCOPE="documentation"
elif echo "$ALL_FILES" | grep -q "src/components\|\.tsx$"; then
    CHANGE_TYPE="feat"
    SCOPE="ui"
elif echo "$ALL_FILES" | grep -q "src/server\|api"; then
    CHANGE_TYPE="feat"
    SCOPE="api"
else
    CHANGE_TYPE="feat"
    SCOPE="core"
fi

# Get summary from git diff
SUMMARY=$(git diff --stat | tail -1 | awk '{print $1 " files changed, " $4 " insertions(+), " $6 " deletions(-)"}')

echo -e "${GREEN}✓ Detected change type: ${CHANGE_TYPE}(${SCOPE})${NC}" >&2
echo -e "${GREEN}✓ Summary: ${SUMMARY}${NC}" >&2

# Step 3: Stage all changes
echo -e "${BLUE}📦 Staging all changes...${NC}" >&2
git add -A

# Step 4: Create commit
echo -e "${BLUE}📝 Creating commit...${NC}" >&2

# Let git hooks handle the commit (pre-commit will run)
# If this script is being called from Claude, let Claude handle the commit
# Otherwise, create a basic commit here
if [ -z "$CLAUDE_CODE_SESSION" ]; then
    git commit -m "$(cat <<EOF
${CHANGE_TYPE}(${SCOPE}): milestone completion

${SUMMARY}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Commit created successfully${NC}" >&2
    else
        echo -e "${RED}✗ Commit failed. Check pre-commit hooks.${NC}" >&2
        exit 1
    fi
fi

# Step 5: Push to remote
echo -e "${BLUE}⬆️  Pushing to remote...${NC}" >&2

CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    echo -e "${YELLOW}⚠ Warning: Pushing to ${CURRENT_BRANCH} branch${NC}" >&2
fi

# Check if branch has upstream
if git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
    git push
else
    git push -u origin "$CURRENT_BRANCH"
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Pushed to origin/${CURRENT_BRANCH}${NC}" >&2
else
    echo -e "${RED}✗ Push failed${NC}" >&2
    exit 1
fi

# Step 6: Document changes
echo -e "${BLUE}📚 Documenting changes...${NC}" >&2

# Create work log entry
cat >> "$WORK_LOG" <<EOF

---

## Milestone: ${TIMESTAMP}

### Branch: ${CURRENT_BRANCH}

### Changes:
${SUMMARY}

### Files Modified:
$(git diff --name-only HEAD~1)

### Commit:
$(git log -1 --oneline)

### Status:
- ✅ Committed and pushed
- 📦 Artifacts archived
- 🧹 Context cleared

EOF

echo -e "${GREEN}✓ Work log updated${NC}" >&2

# Step 7: Archive artifacts
if [ -d "$ARTIFACTS_DIR" ] && [ "$(ls -A $ARTIFACTS_DIR)" ]; then
    echo -e "${BLUE}📁 Archiving artifacts...${NC}" >&2

    mkdir -p "$ARCHIVE_DIR/$TIMESTAMP"
    cp -r "$ARTIFACTS_DIR"/* "$ARCHIVE_DIR/$TIMESTAMP/" 2>/dev/null || true

    echo -e "${GREEN}✓ Artifacts archived to $ARCHIVE_DIR/$TIMESTAMP/${NC}" >&2
fi

# Step 8: Clear artifacts for next phase
echo -e "${BLUE}🧹 Clearing artifacts for next phase...${NC}" >&2

if [ -d "$ARTIFACTS_DIR" ]; then
    # Keep the directory structure but clear contents
    find "$ARTIFACTS_DIR" -type f -delete
    echo -e "${GREEN}✓ Artifacts cleared${NC}" >&2
fi

# Step 9: Update scratchpad with lessons learned
echo -e "${BLUE}📝 Updating scratchpad...${NC}" >&2

cat >> "$SCRATCHPAD" <<EOF

---

## Session: ${TIMESTAMP}

### Completed:
- Milestone work committed and pushed
- Branch: ${CURRENT_BRANCH}
- Commit: $(git log -1 --oneline)

### Next Actions:
- [ ] Review PR (if created)
- [ ] Manual testing
- [ ] Deploy to staging (if applicable)

### Notes:
- Artifacts archived to: $ARCHIVE_DIR/$TIMESTAMP/
- Work log updated
- Context cleared for next phase

EOF

echo -e "${GREEN}✓ Scratchpad updated${NC}" >&2

# Step 10: Summary report
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
echo -e "${GREEN}🎉 Milestone Completion Summary${NC}" >&2
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
echo -e "${GREEN}✓ Changes committed and pushed${NC}" >&2
echo -e "${GREEN}✓ Work documented in ${WORK_LOG}${NC}" >&2
echo -e "${GREEN}✓ Artifacts archived to ${ARCHIVE_DIR}/${TIMESTAMP}/${NC}" >&2
echo -e "${GREEN}✓ Context cleared for next phase${NC}" >&2
echo -e "${GREEN}✓ Scratchpad updated with next actions${NC}" >&2
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n" >&2

# Optional: Create PR if gh CLI is available
if command -v gh >/dev/null 2>&1; then
    echo -e "${YELLOW}💡 Tip: Run 'gh pr create' to create a pull request${NC}" >&2
fi

exit 0
