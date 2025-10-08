# Auto-Implement - Autonomous Scout → Plan → Build

Complete autonomous implementation workflow combining all three phases.

## Purpose

One-command autonomous feature implementation:
1. **Scout**: Identify minimal context
2. **Plan**: Create TDD implementation plan
3. **Build**: Execute plan with specialist agents

**Input**: Feature/bug description
**Output**: Working code, tests, git commits

---

## Usage

```bash
# Basic usage
User: "Auto-implement dark mode toggle in Settings"

# Complex feature
User: "Auto-implement user profile management with avatar upload and bio editing"

# Bug fix
User: "Auto-fix the payment processing timeout issue"

# With documentation
User: "Auto-implement Stripe checkout integration, reference Stripe docs"
```

---

## Workflow

This command chains three sub-workflows:

### Phase 1: Scout (Context Identification)

```
auto-implement → scout-agent
  Task: Identify files and dependencies for feature
  Output: .claude/artifacts/scout-report.md
```

**Scout**:
- Scans codebase (app/, src/, etc.)
- Identifies relevant files with line/byte ranges
- Maps dependencies
- Flags open questions
- Estimates scope

**Pause Point**: User can review scout-report.md before proceeding

---

### Phase 2: Plan (TDD Planning)

```
auto-implement → planner-agent
  Input: scout-report.md
  Task: Create step-by-step TDD plan
  Output: .claude/artifacts/plan.md, design-notes.md
```

**Planner**:
- Reads Scout's minimal context
- Breaks down into < 10 TDD steps
- Defines failing tests for each step
- Estimates token costs
- Defers non-critical work
- May delegate to documentation-expert for API docs

**Pause Point**: User can review/adjust plan.md before execution

---

### Phase 3: Build (TDD Execution)

```
auto-implement → build-executor
  Input: plan.md
  Task: Execute plan step-by-step
  Output: Code, tests, git commits
```

**Builder**:
- For each step:
  1. Write failing test
  2. Delegate implementation to specialist (frontend-developer, backend-architect, etc.)
  3. Run tests (must pass)
  4. Git commit
  5. Pre-commit hook validation
- Stops on any failure

---

## Full Execution Example

**Command**:
```
User: "Auto-implement loading spinner for Dashboard component"
```

**Phase 1: Scout** (~30 seconds)
```
🔍 Scout analyzing codebase...
  ✓ Found Dashboard.tsx
  ✓ Found Spinner.tsx (reusable)
  ✓ Found useDashboardData() hook (has isLoading)
  ✓ Identified 3 files, 2 dependencies
  ✓ Scope: Low complexity, 1 file to modify
📄 Scout report saved to .claude/artifacts/scout-report.md
```

**Pause**: Review scout-report.md (or continue automatically)

**Phase 2: Plan** (~45 seconds)
```
📋 Planner creating TDD implementation plan...
  ✓ Step 1: Test for loading state detection
  ✓ Step 2: Render Spinner when loading
  ✓ Step 3: Hide content during load
  ✓ Estimated: ~800 tokens (3 small steps)
  ✓ Deferred: Skeleton loading, transitions
📄 Plan saved to .claude/artifacts/plan.md
```

**Pause**: Review plan.md (or continue automatically)

**Phase 3: Build** (~3-5 minutes)
```
🏗️  Build-Executor starting TDD workflow...

Step 1/3: Test for loading state detection
  ├─ Create Dashboard.test.tsx
  ├─ Tests: ❌ FAIL (expected)
  ├─ Delegate to test-automator
  ├─ Tests: ✅ PASS
  ├─ Commit: "test: add Dashboard loading state tests"
  └─ Pre-commit: ✅ PASS

Step 2/3: Render Spinner when loading
  ├─ Delegate to frontend-developer
  ├─ Tests: ✅ PASS
  ├─ Commit: "feat: add Spinner to Dashboard during load"
  └─ Pre-commit: ✅ PASS

Step 3/3: Hide content during load
  ├─ Delegate to frontend-developer
  ├─ Tests: ✅ PASS
  ├─ Commit: "feat: hide Dashboard content when loading"
  └─ Pre-commit: ✅ PASS

✅ Auto-Implement Complete!
  Duration: 4m 23s
  Files changed: 2 (Dashboard.tsx, Dashboard.test.tsx)
  Commits: 3
  Tests: 5 passing
  Quality: 85/100
```

---

## Pause Points & Modes

### Interactive Mode (Default)

Pauses for review between phases:

```
Phase 1 Complete → Review scout-report.md → Continue? (y/n)
Phase 2 Complete → Review plan.md → Continue? (y/n)
Phase 3 Executes → Stops on failure
```

### Semi-Autonomous Mode

Only pauses if issues detected:

```
Scout: Auto-continue (unless scope > 10 files)
Plan: Auto-continue (unless steps > 10 or risk = high)
Build: Stops on test failures or hook blocks
```

### Unattended Mode (Sandbox Only) ⚠️

**DO NOT USE ON MAIN BRANCH**

Runs completely hands-off:

```
Scout → Plan → Build (no pauses)
Only stops on critical failures
Requires: isolated branch, container/sandbox, full test coverage
```

To enable:
```bash
# Only in isolated environment!
User: "Auto-implement with no pauses in unattended mode"
```

---

## Stopping & Recovery

### Stop Conditions

Auto-implement halts if:
- ❌ Scout finds > 20 files (scope too large)
- ❌ Planner creates > 15 steps (break into smaller tasks)
- ❌ Plan has high-risk steps (requires manual review)
- ❌ Builder test fails twice on same step
- ❌ Pre-commit hook blocks commit
- ❌ Token budget exhausted

### Recovery

If stopped mid-workflow:

```bash
# Resume from last phase
/plan --scout-report .claude/artifacts/scout-report.md  # Resume at Plan
/build --plan .claude/artifacts/plan.md                # Resume at Build

# Or restart
User: "Auto-implement [task]" # Starts from Scout again
```

---

## Best Use Cases

### ✅ Perfect For
- Well-defined features (dark mode, loading states, CRUD operations)
- Bug fixes with known root cause
- Component additions following existing patterns
- API endpoints with clear contracts
- Refactors with good test coverage

### ⚠️ Use With Caution
- Exploratory work (requirements unclear)
- Breaking changes (API contract changes)
- Large refactors (> 10 files)
- Complex algorithms (needs deep thought)
- Performance optimization (requires profiling)

### ❌ Not Suitable For
- Architecture changes (too complex)
- Greenfield projects (no patterns to follow)
- Security-critical code (needs expert review)
- Database migrations (risky, needs DBA review)
- Production hotfixes (too automated, needs precision)

---

## vs Single-Phase Commands

| Scenario | Use | Instead Of |
|----------|-----|------------|
| New React component | `/create-component` | /auto-implement |
| New API endpoint | `/generate-api` | /auto-implement |
| Deploy to prod | `/deploy` | /auto-implement |
| Complex multi-file feature | `/auto-implement` | Manual workflow |
| Cross-domain feature (UI + API + DB) | `/auto-implement` | Manual workflow |

**Rule of Thumb**:
- 1-2 files → Use specific command (/create-component, /generate-api)
- 3-10 files → Use /auto-implement
- 10+ files → Break into smaller tasks, use /scout → /plan manually

---

## Safety Features

### Built-In Guards

1. **Scope Limiting**: Scout flags if > 10 files
2. **Step Limiting**: Planner breaks into < 10 steps
3. **TDD Enforcement**: Builder requires tests for every step
4. **Quality Gates**: Pre-commit hooks must pass
5. **Failure Halting**: Stops immediately on errors
6. **Token Budgeting**: Warns if approaching limits

### Git Safety

- Every step is a separate commit (atomic, revertable)
- All work on feature branch (never main)
- Pre-commit hooks validate before commit
- Easy to rollback: `git revert <commit-sha>`

---

## Configuration

### Artifact Locations

Change in command to customize:
```markdown
**Output**: `.claude/artifacts/scout-report.md`
→ Change to your preferred path
```

### Pause Behavior

Edit command to adjust pause points:
- Remove pauses for unattended mode
- Add pauses for extra review

---

## Success Criteria

✅ Scout report generated with minimal scope
✅ Plan created with TDD steps
✅ All plan steps executed successfully
✅ Tests passing (100%)
✅ Pre-commit hooks passed
✅ Git commits made (one per step)
✅ Code follows project patterns

---

## Output Artifacts

After completion, review:

```
.claude/artifacts/
├── scout-report.md         # Files analyzed
├── plan.md                 # Implementation steps
└── design-notes.md         # Architecture notes (optional)
```

Git commits:
```bash
git log --oneline
# feat: add loading spinner to Dashboard
# test: add Dashboard loading tests
# feat: hide content during load
```

---

## Notes

- Combines all three workflow phases
- Best for complex features (3-10 files)
- Requires good test coverage to work reliably
- Safe by default (stops on failures)
- Works best with clear, specific requests
- Not a replacement for human oversight - review commits before pushing!

---

## Next Steps After Auto-Implement

1. **Review commits**: `git log -p`
2. **Manual testing**: Verify feature works
3. **Code review**: Check generated code quality
4. **Create PR**: `gh pr create` or push to remote
5. **Deploy** (if approved): `/deploy`
