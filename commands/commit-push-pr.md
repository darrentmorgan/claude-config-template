# Commit, Push, and Create Pull Request

Automated workflow to commit all changes, push to remote, and create a pull request with comprehensive documentation.

## Purpose

This command automates the final steps of a major work phase:
1. Stage and commit all changes with a meaningful message
2. Push to remote repository
3. Create pull request with detailed summary
4. Document changes for future reference
5. Prepare for next work phase

**Use When:**
- Completing a major feature implementation
- Finishing a milestone or sprint task
- Ready to submit work for review
- Transitioning between work phases

---

## Usage

```bash
# Auto-generate commit message and PR
User: "Commit, push, and create PR"

# With custom commit message
User: "Commit with message 'feat: add dark mode toggle' and create PR"

# Specify target branch
User: "Create PR targeting main branch"
```

---

## Workflow

### 1. Pre-Commit Validation

Before committing:
- Run git status to see all changes
- Run git diff to review modifications
- Check for untracked files
- Verify no secrets or credentials in changes
- Warn if large files detected (> 1MB)

### 2. Generate Commit Message

If no message provided, auto-generate from:
- Git diff analysis
- File changes summary
- Type of changes (feat, fix, refactor, test, docs)
- Scope of changes

**Format:**
```
{type}({scope}): {summary}

{detailed description}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Test additions/modifications
- `docs`: Documentation changes
- `chore`: Build/tooling updates

### 3. Create Commit

```bash
git add -A
git commit -m "$(cat <<'EOF'
{generated or provided commit message}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Pre-commit hooks will run:**
- Linting and formatting
- Type checking
- Unit tests
- Code quality checks

**If hooks fail:** Report errors and stop (do not push)

### 4. Push to Remote

```bash
# Get current branch
BRANCH=$(git branch --show-current)

# Check if branch tracks remote
if ! git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
  # First push, set upstream
  git push -u origin $BRANCH
else
  # Branch exists, push normally
  git push origin $BRANCH
fi
```

### 5. Generate PR Summary

Analyze all commits since divergence from base branch:

```bash
# Get commits for PR
BASE_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
git log $BASE_BRANCH..HEAD
git diff $BASE_BRANCH...HEAD
```

**PR Template:**
```markdown
## Summary
{1-3 bullet points of major changes}

## Changes
{List of modified files with brief descriptions}

## Test Plan
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] {Additional test checklist items}

## Related Issues
Closes #{issue-number}

## Screenshots (if UI changes)
{Screenshots or demo GIFs}

## Breaking Changes
{List any breaking changes or migration notes}

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### 6. Create Pull Request

```bash
# Get base branch (main or master)
BASE_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')

# Create PR using GitHub CLI
gh pr create \
  --base "$BASE_BRANCH" \
  --title "{PR title from commit summary}" \
  --body "$(cat <<'EOF'
{Generated PR summary}
EOF
)"
```

**Returns:** PR URL for user to review

### 7. Document Changes

Create or update documentation:

```markdown
# CHANGELOG.md update
## [Unreleased]
### Added
- {New features}

### Changed
- {Modifications}

### Fixed
- {Bug fixes}
```

### 8. Cleanup & Context Reset

- Archive artifacts to `.claude/.archive/{timestamp}/`
- Clear `.claude/artifacts/` for next phase
- Update scratch pads with lessons learned
- Log completion to `.claude/.work-log.md`

---

## Safety Features

### Checks Before Committing

- ❌ Block if secrets detected (.env, credentials, API keys)
- ❌ Block if large binary files added (> 1MB, unless whitelisted)
- ❌ Block if tests failing
- ⚠️ Warn if no tests modified (for feature changes)
- ⚠️ Warn if uncommitted changes in dependencies

### Checks Before Pushing

- ❌ Block if force push to main/master
- ❌ Block if pushing to protected branches (unless authorized)
- ⚠️ Warn if local branch is behind remote
- ⚠️ Warn if merge conflicts detected

### Checks Before PR Creation

- ❌ Block if no commits to include
- ❌ Block if branch name is main/master
- ⚠️ Warn if PR already exists for branch
- ⚠️ Warn if base branch has new commits

---

## Configuration

### Commit Message Templates

In `.claude/settings.local.json`:

```json
{
  "commit_templates": {
    "feat": "feat({scope}): {summary}",
    "fix": "fix({scope}): {summary}",
    "refactor": "refactor({scope}): {summary}",
    "test": "test: {summary}",
    "docs": "docs: {summary}"
  }
}
```

### PR Templates

In `.claude/pr-template.md`:

```markdown
## Summary
{summary}

## Test Plan
{test_plan}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Protected Branches

In `.claude/settings.local.json`:

```json
{
  "protected_branches": ["main", "master", "production"],
  "require_pr_approval": true,
  "min_approvals": 1
}
```

---

## Examples

### Example 1: Feature Completion

```bash
User: "Commit and create PR for the dark mode feature"

Output:
✓ Staged 8 files (4 new, 4 modified)
✓ Created commit: "feat(ui): add dark mode toggle to settings"
✓ Pushed to origin/feature/dark-mode
✓ Created PR: https://github.com/user/repo/pull/42
✓ Archived artifacts to .claude/.archive/2025-10-10-14-23/
✓ Ready for next phase
```

### Example 2: Bug Fix

```bash
User: "Commit and PR for auth bug fix"

Output:
✓ Analyzed changes: 2 files modified
✓ Created commit: "fix(auth): resolve token refresh race condition"
✓ Pushed to origin/fix/auth-token-race
✓ Created PR: https://github.com/user/repo/pull/43
  Title: "Fix auth token refresh race condition"
  Closes: #127
✓ Updated CHANGELOG.md
```

### Example 3: Multiple Commits

```bash
User: "Create PR with all commits from this branch"

Output:
✓ Found 5 commits since main:
  - feat: add user preferences
  - test: add preferences tests
  - refactor: simplify preference store
  - docs: update API docs
  - fix: handle empty preferences
✓ All commits already pushed
✓ Created PR with comprehensive summary
✓ PR: https://github.com/user/repo/pull/44
```

---

## Error Handling

### Pre-commit Hook Failure

```
❌ Pre-commit hook failed

Error: ESLint found 3 errors
  src/Settings.tsx:23 - unused variable
  src/theme.ts:45 - missing return type

Action: Fix errors before committing
```

### Push Failure

```
❌ Push failed

Error: Updates were rejected (remote has newer commits)

Action: Pull latest changes first
  git pull origin feature/dark-mode --rebase
```

### PR Creation Failure

```
❌ PR creation failed

Error: PR already exists for this branch (#42)

Action: Update existing PR or create new branch
```

---

## Integration with Hooks

This command works with existing hooks:

- **pre-commit.sh**: Runs quality gates
- **post-commit.sh**: Logs commit details
- **post-milestone.sh**: Can auto-trigger this command

---

## Best Practices

### ✅ Do

- Review changes before committing
- Write meaningful commit messages
- Include test updates
- Update documentation
- Create focused PRs (one feature/fix)

### ❌ Don't

- Commit secrets or credentials
- Create massive PRs (> 10 files)
- Skip tests
- Force push to main
- Bypass hooks without reason

---

## See Also

- [Git Workflow](../docs/WORKFLOWS.md)
- [PR Review Guide](../docs/PR_REVIEW.md)
- [Hooks System](../hooks/README.md)

---

**Version:** 1.0.0
**Last Updated:** 2025-10-10
**Status:** ✅ Production Ready
