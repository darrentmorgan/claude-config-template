# Branch Protection & Auto-Merge Setup Guide

This guide explains how to configure GitHub repository settings to enable automated PR testing, required checks, and auto-merge functionality.

## Table of Contents

- [Branch Protection Rules](#branch-protection-rules)
- [Required Workflows](#required-workflows)
- [Auto-Merge Configuration](#auto-merge-configuration)
- [Permissions & Tokens](#permissions--tokens)
- [Usage Instructions](#usage-instructions)
- [Troubleshooting](#troubleshooting)

---

## Branch Protection Rules

### Enable Branch Protection for `main`

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Branches**
3. Under "Branch protection rules", click **Add rule**
4. Configure the following settings:

#### Branch Name Pattern
```
main
```

#### Protection Settings

**Require a pull request before merging:**
- ✅ Enable this option
- ✅ Require approvals: **1** (minimum)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners (optional, if you have CODEOWNERS file)

**Require status checks to pass before merging:**
- ✅ Enable this option
- ✅ Require branches to be up to date before merging
- Add required status checks:
  - `Test & Validate`
  - `Security & Dependency Audit`

**Require conversation resolution before merging:**
- ✅ Enable this option (recommended)

**Require linear history:**
- ✅ Enable this option (enforces squash/rebase, no merge commits)

**Do not allow bypassing the above settings:**
- ✅ Enable this option (recommended for production)
- Note: Admins can still bypass if needed

**Allow force pushes:**
- ❌ Disable this option (recommended)

**Allow deletions:**
- ❌ Disable this option (recommended)

---

## Required Workflows

The following workflows are included in this repository:

### 1. PR Testing Workflow (`.github/workflows/pr-tests.yml`)

**Triggers:** Pull requests to `main` or `develop` branches

**What it does:**
- Validates TypeScript compilation
- Runs type checking across the project
- Validates shell script syntax
- Validates JSON configuration files
- Checks for required project files
- Runs test suite (if configured)
- Posts test results as PR comments
- Runs security scans (npm audit, secret detection)

**Required Status Checks:**
- `Test & Validate`
- `Security & Dependency Audit`

### 2. Auto-Merge Workflow (`.github/workflows/auto-merge.yml`)

**Triggers:**
- PR review submitted
- Check suite completed
- PR labeled with `auto-merge`

**What it does:**
- Validates all required checks passed
- Ensures PR has required approvals (≥1)
- Checks for merge conflicts
- Verifies author permissions (for main branch)
- Auto-merges PR using squash merge
- Posts success comment

**Security Features:**
- Only trusted authors can auto-merge to `main`
- Dependabot PRs auto-merge when checks pass
- Blocks PRs with conflicts or failing checks

---

## Auto-Merge Configuration

### Enable Auto-Merge Feature in Repository

1. Go to **Settings** → **General**
2. Scroll to "Pull Requests" section
3. Enable the following:
   - ✅ **Allow auto-merge**
   - ✅ **Automatically delete head branches** (recommended)
   - ✅ **Allow squash merging** (primary merge method)
   - ❌ **Allow merge commits** (optional, disable for linear history)
   - ❌ **Allow rebase merging** (optional)

### Using Auto-Merge

#### Option 1: Add Label
Add the `auto-merge` label to your PR:

```bash
gh pr edit <PR_NUMBER> --add-label "auto-merge"
```

Or via GitHub UI:
1. Open the PR
2. Add label: `auto-merge`
3. Wait for checks to pass and get approval

#### Option 2: Dependabot (Automatic)
Dependabot PRs will automatically merge when:
- All required checks pass
- No merge conflicts

#### Option 3: Manual Trigger
The workflow automatically runs when:
- A PR receives an approval review
- All check suites complete successfully

### Auto-Merge Conditions

A PR will auto-merge when ALL of these conditions are met:

1. ✅ All required status checks passed
2. ✅ At least 1 approval review (not required for Dependabot)
3. ✅ No merge conflicts
4. ✅ Has `auto-merge` label OR is from `dependabot[bot]`
5. ✅ Author has write permissions (for main branch merges)
6. ✅ PR is not in draft state

---

## Permissions & Tokens

### GitHub Token Permissions

The workflows use the default `GITHUB_TOKEN` which requires the following permissions:

**For `pr-tests.yml`:**
- `contents: read` - Checkout code
- `pull-requests: write` - Post comments on PRs
- `checks: write` - Create check runs

**For `auto-merge.yml`:**
- `contents: write` - Merge PRs
- `pull-requests: write` - Comment on PRs
- `checks: read` - Read check status

### Default Token Configuration

The `GITHUB_TOKEN` is automatically provided by GitHub Actions and has these permissions by default. No additional secrets are required.

### Modifying Permissions

If you need to customize permissions:

1. Go to **Settings** → **Actions** → **General**
2. Under "Workflow permissions":
   - Choose "Read and write permissions" (default for public repos)
   - ✅ Enable "Allow GitHub Actions to create and approve pull requests"

---

## Usage Instructions

### For Developers

#### 1. Create a Pull Request

```bash
git checkout -b feature/my-feature
# Make changes
git commit -m "feat: add new feature"
git push origin feature/my-feature
gh pr create --title "Add new feature" --body "Description"
```

#### 2. Enable Auto-Merge

```bash
# Add the auto-merge label
gh pr edit --add-label "auto-merge"
```

Or via GitHub UI:
1. Open your PR
2. Click "Labels" on the right sidebar
3. Select `auto-merge`

#### 3. Wait for Checks & Approval

The PR will automatically merge when:
- All tests pass
- Security scan passes
- At least 1 approval received

#### 4. Monitor Progress

Check the "Checks" tab on your PR to see:
- Test results
- Security scan results
- Auto-merge status

### For Reviewers

#### Approve a PR

```bash
gh pr review <PR_NUMBER> --approve --body "LGTM!"
```

Or via GitHub UI:
1. Open the PR
2. Go to "Files changed"
3. Click "Review changes" → "Approve"

The PR will auto-merge if:
- It has the `auto-merge` label
- All checks passed
- No conflicts

---

## Troubleshooting

### Auto-Merge Not Triggering

**Check:**
1. ✅ Does PR have `auto-merge` label?
2. ✅ Are all required checks passing?
3. ✅ Does PR have at least 1 approval?
4. ✅ Are there merge conflicts?
5. ✅ Is PR in draft state?

**View workflow logs:**
```bash
gh run list --workflow=auto-merge.yml
gh run view <RUN_ID> --log
```

### Tests Failing

**View test results:**
- Check PR comments for test report
- View "Checks" tab on PR
- Review workflow logs:

```bash
gh run list --workflow=pr-tests.yml
gh run view <RUN_ID> --log
```

**Common issues:**
- TypeScript compilation errors
- Shell script syntax errors
- Invalid JSON in configuration files
- Missing required files
- npm audit vulnerabilities

### Security Scan Failures

**npm audit failures:**
```bash
# Run locally
npm audit

# Fix automatically
npm audit fix

# Fix with breaking changes
npm audit fix --force
```

**Secret detection:**
- Review the diff for hardcoded credentials
- Use environment variables or secrets management
- Never commit API keys, tokens, or passwords

### Permission Errors

**Error:** "Author does not have permission to auto-merge"

**Solution:**
1. Verify author has write access to repository
2. For main branch, only trusted collaborators can auto-merge
3. Contact repository admin for access

### Merge Conflicts

**Error:** "PR has merge conflicts"

**Solution:**
```bash
# Update your branch
git checkout feature/my-feature
git fetch origin
git rebase origin/main

# Resolve conflicts
# ... fix conflicts ...
git add .
git rebase --continue

# Force push (safe for feature branches)
git push --force-with-lease
```

---

## Advanced Configuration

### Custom Status Checks

To add more required checks:

1. Edit `.github/workflows/pr-tests.yml`
2. Add new job:

```yaml
custom-check:
  name: Custom Validation
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run custom validation
      run: ./scripts/custom-validation.sh
```

3. Update branch protection rules to require new check

### Modify Auto-Merge Behavior

Edit `.github/workflows/auto-merge.yml`:

**Change minimum approvals:**
```javascript
const approvals = Object.values(reviewsByUser).filter(
  review => review.state === 'APPROVED'
).length;

// Change this line:
core.setOutput('approved', approvals >= 2 ? 'true' : 'false');  // Require 2 approvals
```

**Change merge method:**
```javascript
await github.rest.pulls.merge({
  owner: context.repo.owner,
  repo: context.repo.repo,
  pull_number: prNumber,
  merge_method: 'rebase',  // Options: 'merge', 'squash', 'rebase'
});
```

### Disable Auto-Merge for Certain Branches

Edit the workflow condition:

```yaml
if: |
  github.event_name == 'pull_request_review' ||
  github.event_name == 'check_suite' ||
  (github.event_name == 'pull_request' &&
   github.event.label.name == 'auto-merge' &&
   github.base_ref != 'production')  # Disable for production branch
```

---

## Best Practices

1. **Always use PR workflow** - Never push directly to main
2. **Keep branches up to date** - Rebase or merge main regularly
3. **Use semantic commits** - Follow conventional commits format
4. **Review before auto-merge** - Don't blindly approve PRs
5. **Monitor security scans** - Fix vulnerabilities promptly
6. **Keep workflows updated** - Review and update workflows quarterly
7. **Test locally first** - Run tests before pushing

---

## Additional Resources

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Auto-Merge Documentation](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security/getting-started/securing-your-repository)

---

## Support

For issues or questions:

1. Check workflow logs: `gh run list`
2. Review this documentation
3. Check GitHub Actions status: https://www.githubstatus.com/
4. Create an issue in this repository

---

**Last Updated:** 2025-10-10
**Maintained by:** Darren Morgan
