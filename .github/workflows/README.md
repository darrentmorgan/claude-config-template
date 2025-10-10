# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the repository.

## Available Workflows

### 1. PR Testing (`pr-tests.yml`)

Automatically runs quality gates on all pull requests to ensure code quality and security.

**Triggers:**
- Pull request opened, updated, or reopened
- Target branches: `main`, `develop`

**Jobs:**

#### Test & Validate
- TypeScript compilation check
- Type checking (project-wide)
- Shell script syntax validation
- JSON configuration validation
- Required files verification
- Test suite execution
- Automated PR comments with results

#### Security & Dependency Audit
- npm audit for dependency vulnerabilities
- Secret detection in code changes
- Security vulnerability reporting

**Required for merge:** ✅ Yes

---

### 2. Auto-Merge (`auto-merge.yml`)

Automatically merges approved pull requests when all checks pass.

**Triggers:**
- PR review submitted (approval)
- Check suite completed
- PR labeled with `auto-merge`

**Behavior:**
- Validates all required checks passed
- Ensures minimum 1 approval (not required for Dependabot)
- Checks for merge conflicts
- Verifies author permissions for protected branches
- Merges using squash method
- Posts success comment

**Security Features:**
- Only trusted collaborators can auto-merge to `main`
- Dependabot PRs auto-merge when checks pass
- Blocks untrusted authors from merging to protected branches

---

## Setup Instructions

### 1. Enable Workflows

Workflows are automatically enabled when merged to the default branch.

### 2. Configure Branch Protection

See [Branch Protection Guide](../../docs/BRANCH_PROTECTION.md) for detailed setup instructions.

**Quick Setup:**
1. Go to **Settings** → **Branches**
2. Add rule for `main` branch
3. Enable:
   - Require pull request reviews (≥1)
   - Require status checks: `Test & Validate`, `Security & Dependency Audit`
   - Require linear history
4. Go to **Settings** → **General** → **Pull Requests**
5. Enable "Allow auto-merge"

### 3. Create `auto-merge` Label

```bash
gh label create auto-merge --description "Automatically merge when checks pass" --color "0E8A16"
```

Or via GitHub UI:
1. Go to **Issues** → **Labels**
2. Click **New label**
3. Name: `auto-merge`
4. Color: Green (`#0E8A16`)
5. Description: "Automatically merge when checks pass"

---

## Usage

### For Pull Request Authors

**Enable auto-merge on your PR:**

```bash
# Create PR
gh pr create --title "Your title" --body "Description"

# Add auto-merge label
gh pr edit --add-label "auto-merge"
```

Your PR will automatically merge when:
- All tests pass
- Security scans pass
- At least 1 approval received
- No merge conflicts

### For Reviewers

**Approve a PR:**

```bash
gh pr review <PR_NUMBER> --approve
```

The PR will auto-merge if it has the `auto-merge` label and all checks pass.

---

## Workflow Permissions

Both workflows use the default `GITHUB_TOKEN` with these permissions:

**pr-tests.yml:**
- `contents: read` - Checkout code
- `pull-requests: write` - Post comments
- `checks: write` - Create check runs

**auto-merge.yml:**
- `contents: write` - Merge PRs
- `pull-requests: write` - Comment on PRs
- `checks: read` - Read check status

No additional secrets required.

---

## Quality Gates

All PRs must pass these checks:

### TypeScript Validation
- Scripts must compile without errors
- Type checking must pass

### Shell Script Validation
- All `.sh` files must have valid syntax
- Tested with `bash -n`

### Configuration Validation
- All JSON files must be valid
- Python JSON parser validation

### Required Files
- `.claude/agents/delegation-map.json`
- `.claude/settings.local.json`
- `package.json`
- `hooks/pre-commit.sh`

### Security Checks
- No npm audit vulnerabilities (moderate+)
- No hardcoded secrets in code

---

## Customization

### Add New Test Jobs

Edit `pr-tests.yml`:

```yaml
custom-test:
  name: Custom Test
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run custom test
      run: npm run custom-test
```

### Modify Auto-Merge Conditions

Edit `auto-merge.yml`:

**Require more approvals:**
```javascript
// Change from ≥1 to ≥2
core.setOutput('approved', approvals >= 2 ? 'true' : 'false');
```

**Change merge method:**
```javascript
merge_method: 'rebase',  // Options: merge, squash, rebase
```

---

## Troubleshooting

### View Workflow Runs

```bash
# List recent runs
gh run list

# View specific run
gh run view <RUN_ID> --log

# View workflow-specific runs
gh run list --workflow=pr-tests.yml
gh run list --workflow=auto-merge.yml
```

### Common Issues

**Tests not running:**
- Check if workflow file has syntax errors
- Verify triggers match your branch/event
- Check repository Actions settings are enabled

**Auto-merge not working:**
- Verify `auto-merge` label exists and is applied
- Check all required status checks passed
- Ensure PR has required approvals
- Verify no merge conflicts

**Permission errors:**
- Check workflow permissions in repository settings
- Verify `GITHUB_TOKEN` has required permissions
- For main branch, verify author has write access

---

## Best Practices

1. **Always run tests locally** before pushing
2. **Keep workflows fast** - optimize for quick feedback
3. **Use caching** for dependencies (already configured)
4. **Monitor workflow usage** - GitHub has monthly limits
5. **Keep workflows updated** - review quarterly
6. **Use concurrency limits** - prevents duplicate runs
7. **Add timeouts** - prevents hanging jobs

---

## Monitoring & Maintenance

### Check Workflow Health

```bash
# View recent runs
gh run list --limit 10

# Check for failures
gh run list --status failure
```

### Update Actions

Workflows use specific action versions. Update periodically:

```yaml
# Current versions
actions/checkout@v4
actions/setup-node@v4
actions/github-script@v7
```

Check for updates at: https://github.com/actions

### Performance Optimization

Current optimizations:
- ✅ Dependency caching enabled
- ✅ Concurrency limits prevent duplicate runs
- ✅ Timeouts prevent hanging jobs (15min test, 10min security)
- ✅ Parallel job execution where possible

---

## Security Considerations

### Workflow Injection Prevention

All workflows follow security best practices:

**✅ Safe Pattern (Used):**
```yaml
env:
  USER_INPUT: ${{ github.event.pull_request.title }}
run: echo "$USER_INPUT"
```

**❌ Unsafe Pattern (Avoided):**
```yaml
run: echo "${{ github.event.pull_request.title }}"
```

### Secret Scanning

The `pr-tests.yml` workflow includes basic secret detection:
- Scans for API keys, tokens, passwords
- Fails PR if potential secrets found
- Patterns: `api_key`, `secret`, `password`, `token`, `private_key`

**For production**, consider:
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)
- [Gitleaks](https://github.com/zricethezav/gitleaks)
- [TruffleHog](https://github.com/trufflesecurity/trufflehog)

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Branch Protection Setup](../../docs/BRANCH_PROTECTION.md)
- [Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

---

**Maintained by:** Darren Morgan
**Last Updated:** 2025-10-10
