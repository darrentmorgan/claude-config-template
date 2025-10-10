# Quick Start: Enable Auto-Merge

This guide will help you enable auto-merge functionality in under 5 minutes.

## Prerequisites

- Repository admin access
- GitHub CLI installed (optional, but recommended)

---

## Step 1: Enable Repository Settings (2 minutes)

### Via GitHub UI:

1. **Navigate to Settings** → **General** → **Pull Requests**

2. **Enable these options:**
   - ✅ Allow auto-merge
   - ✅ Allow squash merging
   - ✅ Automatically delete head branches

3. **Click "Save changes"**

---

## Step 2: Set Up Branch Protection (3 minutes)

### Via GitHub UI:

1. **Navigate to Settings** → **Branches**

2. **Click "Add rule"** under "Branch protection rules"

3. **Branch name pattern:** `main`

4. **Enable these protections:**
   - ✅ Require a pull request before merging
     - Require approvals: **1**
   - ✅ Require status checks to pass before merging
     - Add checks:
       - `Test & Validate`
       - `Security & Dependency Audit`
   - ✅ Require linear history

5. **Click "Create"** or **"Save changes"**

### Or via GitHub CLI:

```bash
# Set branch protection
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_pull_request_reviews[required_approving_review_count]=1 \
  --field required_status_checks[strict]=true \
  --field required_status_checks[checks][][context]="Test & Validate" \
  --field required_status_checks[checks][][context]="Security & Dependency Audit" \
  --field enforce_admins=false \
  --field required_linear_history=true
```

---

## Step 3: Create Auto-Merge Label (30 seconds)

### Via GitHub CLI:

```bash
gh label create auto-merge \
  --description "Automatically merge when checks pass" \
  --color "0E8A16"
```

### Or via GitHub UI:

1. **Navigate to Issues** → **Labels**
2. **Click "New label"**
3. **Fill in:**
   - Name: `auto-merge`
   - Description: `Automatically merge when checks pass`
   - Color: `#0E8A16` (green)
4. **Click "Create label"**

---

## Step 4: Enable Workflow Permissions (30 seconds)

1. **Navigate to Settings** → **Actions** → **General**

2. **Under "Workflow permissions":**
   - Select: **"Read and write permissions"**
   - ✅ Enable "Allow GitHub Actions to create and approve pull requests"

3. **Click "Save"**

---

## ✅ You're Done!

Auto-merge is now enabled. Here's how to use it:

### For PR Authors:

```bash
# Create a PR
gh pr create --title "Add new feature" --body "Description"

# Add auto-merge label
gh pr edit --add-label "auto-merge"
```

### What Happens Next:

1. ⚙️ Automated tests run
2. 👀 Reviewer approves PR
3. ✅ All checks pass
4. 🚀 PR auto-merges with squash commit
5. 🧹 Branch auto-deletes

---

## Testing the Setup

Create a test PR to verify everything works:

```bash
# Create test branch
git checkout -b test/auto-merge-setup

# Make a small change
echo "# Test" >> TEST.md
git add TEST.md
git commit -m "test: verify auto-merge setup"

# Push and create PR
git push origin test/auto-merge-setup
gh pr create --title "Test auto-merge" --body "Testing auto-merge functionality"

# Add label
gh pr edit --add-label "auto-merge"

# Approve (if you have permissions)
gh pr review --approve
```

Watch the PR auto-merge when checks pass!

---

## Troubleshooting

### Auto-merge not working?

**Check:**
1. Does PR have `auto-merge` label? → `gh pr view --json labels`
2. Are checks passing? → `gh pr checks`
3. Is PR approved? → `gh pr view --json reviews`
4. Any conflicts? → `gh pr view --json mergeable`

**View workflow logs:**
```bash
gh run list --workflow=auto-merge.yml
```

### Tests failing?

```bash
# View test results
gh run list --workflow=pr-tests.yml

# Check specific run
gh run view <RUN_ID> --log
```

---

## Next Steps

- 📚 Read the [full documentation](../docs/BRANCH_PROTECTION.md)
- 🔧 [Customize workflows](.github/workflows/README.md)
- 🔐 Review [security considerations](../docs/BRANCH_PROTECTION.md#security-considerations)

---

## Common Commands

```bash
# Create PR with auto-merge
gh pr create --title "..." --body "..." && gh pr edit --add-label "auto-merge"

# Check PR status
gh pr status

# View PR checks
gh pr checks

# Approve PR
gh pr review --approve

# Remove auto-merge
gh pr edit --remove-label "auto-merge"

# View workflow runs
gh run list

# Re-run failed workflows
gh run rerun <RUN_ID>
```

---

**Need help?** See [Branch Protection Guide](../docs/BRANCH_PROTECTION.md) or create an issue.
