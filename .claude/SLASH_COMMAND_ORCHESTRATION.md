# Slash Command Orchestration System

## 🎯 Overview

This system prevents **agent recursion memory leaks** by using slash commands as an orchestration layer instead of direct agent-to-agent delegation.

### Key Innovation
- Agents execute **slash commands**, not other agents
- Slash commands can spawn **parallel processes** with timeouts
- **Structured outputs only** (file paths with line ranges, not full content)
- **No infinite loops** - agents can't use Task tool
- **Variable injection** - commands share state via `.claude/.variables.json`

---

## 📋 Workflow Commands

### 1. `/scout` - Parallel File Discovery
**Purpose:** Find relevant files using multiple fast agents in parallel

**Usage:**
```bash
/scout "Add user authentication to login page" "4"
```

**How it works:**
1. Spawns 3-5 parallel search agents (gemini, opencode, claude, etc.)
2. Each agent has 3-minute timeout
3. Agents search codebase using their own tools
4. Results merged and deduplicated
5. Outputs structured list: `path/to/file (offset: N, limit: M)`

**Output:** `.claude/.scout-results.txt`

**Key Rules:**
- Agents CANNOT use Task tool
- Agents ONLY call external CLI tools via Bash
- Skip agents that timeout (don't restart)
- Return file paths with line ranges only

---

### 2. `/plan_w_docs` - Implementation Planning
**Purpose:** Create step-by-step plan based on scout results

**Usage:**
```bash
/plan_w_docs "Add user auth..." "https://docs..." ".claude/.scout-results.txt"
```

**How it works:**
1. Reads scout results
2. Reads ONLY specified line ranges from each file
3. Fetches documentation if URLs provided
4. Analyzes architecture
5. Creates implementation plan

**Output:** `.claude/.plan.md`

**Key Rules:**
- NO Task tool delegation
- Read files with offset/limit (not entire files)
- Output structured plan with:
  - Files to modify
  - Changes per file
  - Implementation order
  - Recommended agent

---

### 3. `/build` - Execute Plan
**Purpose:** Delegate to specialized agent to implement plan

**Usage:**
```bash
/build ".claude/.plan.md"
```

**How it works:**
1. Reads plan
2. Selects appropriate agent (frontend-developer, backend-architect, etc.)
3. Delegates ONCE via Task tool
4. Agent implements ALL changes in plan
5. Agent calls `/review` when done

**Key Rules:**
- **Building agent CANNOT delegate** (Task tool blocked)
- Agent MUST implement entire plan
- Agent can ONLY call `/review` slash command
- NO stopping midway

---

### 4. `/review` - Quality Gate
**Purpose:** Code review with code-reviewer-pro

**Usage:**
```bash
/review  # auto-detects modified files
# OR
/review "src/Login.tsx,src/authService.ts"
```

**How it works:**
1. Detects modified files (git status) or uses provided list
2. Delegates to code-reviewer-pro
3. Reviews each file for quality, security, performance
4. Outputs structured report
5. Auto-suggests `/fix` if issues found

**Output:** `.claude/.review-report.md`

**Key Rules:**
- code-reviewer-pro CANNOT modify files (read-only)
- CANNOT delegate to other agents
- MUST output severity for each issue (critical/warning/suggestion)

---

### 5. `/fix` - Issue Resolution
**Purpose:** Fix issues from code review

**Usage:**
```bash
/fix ".claude/.review-report.md"
```

**How it works:**
1. Reads review report
2. Delegates to same agent that did `/build`
3. Agent fixes ALL issues
4. Automatically calls `/review` again
5. Maximum 2 fix→review cycles

**Key Rules:**
- Fixing agent CANNOT delegate
- MUST fix critical and warning issues
- Auto-calls `/review` after fixes
- Prevents infinite loops (max 2 attempts)

---

### 6. `/scout_plan_build` - Full Workflow
**Purpose:** Orchestrate complete scout→plan→build→review cycle

**Usage:**
```bash
/scout_plan_build "Add user authentication" "https://auth-docs.com"
```

**How it works:**
1. Calls `/scout` with task
2. Calls `/plan_w_docs` with scout results
3. Calls `/build` with plan
4. `/build` agent auto-calls `/review`
5. If issues found, auto-calls `/fix`
6. Reports final results

**Key Rules:**
- Execute steps in order
- Wait for each step to complete
- DO NOT stop between steps
- Report comprehensive summary at end

---

## 🔧 Variable System

### State File: `.claude/.variables.json`

```json
{
  "TASK": "Add user authentication",
  "FILE_LIST": ".claude/.scout-results.txt",
  "PLAN_PATH": ".claude/.plan.md",
  "REVIEW_REPORT": ".claude/.review-report.md",
  "CURRENT_STEP": "build",
  "WORKFLOW_STATUS": "in_progress",
  "MODIFIED_FILES": ["src/Login.tsx", "src/authService.ts"],
  "CURRENT_AGENT": "frontend-developer",
  "FIX_ATTEMPTS": 0,
  "LAST_UPDATED": "2025-10-09T20:30:00Z"
}
```

### Variable Injection

**Pre-slash-command hook** injects variables:
```bash
.claude/scripts/inject-variables.sh command_file
```

Replaces in command prompts:
- `$TASK` → actual task description
- `$FILE_LIST` → path to scout results
- `$PLAN_PATH` → path to plan
- `$REVIEW_REPORT` → path to review

### Variable Updates

**Post-slash-command hook** updates state:
```bash
.claude/scripts/update-variables.sh "CURRENT_STEP" "plan"
.claude/scripts/update-variables.sh "FILE_LIST" ".claude/.scout-results.txt"
```

---

## 🛡️ Agent Restrictions

### Restriction Enforcement

Agents are blocked from using Task tool (except orchestrator):

**.claude/agents/configs/frontend-developer.json:**
```json
{
  "name": "frontend-developer",
  "blockedTools": ["Task"],
  "allowedSlashCommands": ["/review"],
  "maxDelegations": 0
}
```

### Agent Permissions Matrix

| Agent | Task Tool | Allowed Slash Commands | Can Delegate |
|-------|-----------|----------------------|--------------|
| Orchestrator (main) | ✅ | All | Yes (via slash commands) |
| frontend-developer | ❌ | `/review` only | No |
| backend-architect | ❌ | `/review` only | No |
| test-automator | ❌ | `/review` only | No |
| code-reviewer-pro | ❌ | `/fix` only | No |
| typescript-pro | ❌ | `/review` only | No |

### How Blocking Works

**In `.claude/settings.local.json`:**
```json
{
  "permissions": {
    "deny": [
      "Task(*:frontend-developer:*)",
      "Task(*:backend-architect:*)",
      "Task(*:code-reviewer-pro:*)"
    ]
  }
}
```

This prevents agents from calling Task tool, forcing them to only use allowed tools and slash commands.

---

## 🔄 Workflow Example

```
User: /scout_plan_build "Add login page with auth"

┌─────────────────────────────────────────┐
│ 1. SCOUT (Parallel)                     │
├─────────────────────────────────────────┤
│ → gemini agent (3min timeout)           │
│ → opencode agent (3min timeout)         │
│ → claude agent (3min timeout)           │
│ → codex agent (3min timeout)            │
│                                          │
│ Results merged → .claude/.scout-results.txt │
│                                          │
│ Found: 5 files                           │
│ - src/components/Login.tsx (45-75)      │
│ - src/services/auth.ts (1-50)           │
│ - src/hooks/useAuth.ts (10-40)          │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 2. PLAN                                  │
├─────────────────────────────────────────┤
│ Reads scout results                      │
│ Reads lines 45-75 of Login.tsx          │
│ Reads lines 1-50 of auth.ts              │
│ Analyzes architecture                    │
│                                          │
│ Creates plan → .claude/.plan.md          │
│                                          │
│ Recommends: frontend-developer           │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 3. BUILD                                 │
├─────────────────────────────────────────┤
│ Reads plan                               │
│ Delegates to: frontend-developer         │
│                                          │
│ frontend-developer:                      │
│ ✓ Implements auth state                 │
│ ✓ Updates Login.tsx                     │
│ ✓ Modifies auth.ts                      │
│ ✓ All changes complete                  │
│ → Calls /review                          │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 4. REVIEW                                │
├─────────────────────────────────────────┤
│ Delegates to: code-reviewer-pro          │
│                                          │
│ Checks:                                  │
│ ✓ Code quality                           │
│ ✓ Type safety                            │
│ ✓ Security                               │
│ ✗ Found 2 issues                         │
│                                          │
│ Report → .claude/.review-report.md       │
│ → Auto-calls /fix                        │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 5. FIX                                   │
├─────────────────────────────────────────┤
│ Reads review report                      │
│ Delegates to: frontend-developer         │
│                                          │
│ frontend-developer:                      │
│ ✓ Fixed missing error handling          │
│ ✓ Fixed type safety issue                │
│ → Calls /review                          │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 6. REVIEW (2nd attempt)                  │
├─────────────────────────────────────────┤
│ Delegates to: code-reviewer-pro          │
│                                          │
│ ✅ NO ISSUES FOUND                       │
│                                          │
│ Workflow COMPLETE                        │
└─────────────────────────────────────────┘

Final Report:
✅ Task complete
Files modified: 3
Issues fixed: 2
Total time: 8 minutes
```

---

## 🚀 Benefits

### Memory Safety
- ✅ No agent recursion (Task tool blocked for workers)
- ✅ Timeouts prevent hangs (3min max)
- ✅ Parallel execution uses less memory per agent
- ✅ Structured outputs only (no full files in memory)

### Performance
- ✅ 5x faster scouting (parallel agents)
- ✅ Token efficient (line ranges only)
- ✅ Skip slow agents (timeout and continue)
- ✅ Results cached to files

### Debugging
- ✅ Clear workflow steps (scout→plan→build→review)
- ✅ State tracking (`.variables.json`)
- ✅ Isolated failures (fix one step without restarting all)
- ✅ Hook logs show transitions

### Flexibility
- ✅ Composable (use `/scout` + `/plan` OR just `/build`)
- ✅ Agent swapping (change which agent does `/build`)
- ✅ Custom workflows (create `/hotfix`, `/refactor`, etc.)
- ✅ Hook extensibility (add monitoring, notifications)

---

## 📁 File Structure

```
.claude/
├── commands/
│   ├── scout.md                    # Parallel file discovery
│   ├── plan_w_docs.md             # Implementation planning
│   ├── build.md                    # Execute plan
│   ├── review.md                   # Quality gate
│   ├── fix.md                      # Issue resolution
│   └── scout_plan_build.md        # Full workflow orchestrator
│
├── scripts/
│   ├── inject-variables.sh         # Variable substitution
│   └── update-variables.sh         # State updates
│
├── hooks/
│   ├── post-slash-command.sh       # Chain commands
│   └── pre-slash-command.sh        # Inject variables
│
├── agents/configs/
│   ├── frontend-developer.json     # Task tool blocked
│   ├── backend-architect.json      # Task tool blocked
│   └── code-reviewer-pro.json      # Task tool blocked
│
└── (state files)
    ├── .variables.json             # Shared state
    ├── .scout-results.txt          # Scout output
    ├── .plan.md                    # Plan output
    └── .review-report.md           # Review output
```

---

## 🎓 Best Practices

### 1. Use Full Workflow for New Features
```bash
/scout_plan_build "Add user registration" "https://docs.auth.com"
```

### 2. Use Individual Commands for Targeted Work
```bash
# If you know files to modify:
/plan_w_docs "Fix login bug" "" "src/Login.tsx,src/auth.ts"
/build ".claude/.plan.md"
```

### 3. Monitor State During Execution
```bash
# In separate terminal:
watch -n 2 cat .claude/.variables.json
```

### 4. Review Outputs Between Steps
```bash
# After scout:
cat .claude/.scout-results.txt

# After plan:
cat .claude/.plan.md

# After review:
cat .claude/.review-report.md
```

### 5. Handle Failures Gracefully
- Scout fails → Manually specify files in `/plan_w_docs`
- Plan fails → Add more documentation URLs or context
- Build fails → Check `.plan.md` for clarity
- Review fails → `/fix` runs automatically

---

## 🔍 Troubleshooting

### "Agent trying to use Task tool"
- Check agent config has `"blockedTools": ["Task"]`
- Verify permissions in settings.local.json deny Task for that agent

### "Slash command not found"
- Check file exists in `.claude/commands/`
- Verify filename matches command (e.g., `scout.md` for `/scout`)

### "Variables not substituting"
- Ensure `pre-slash-command.sh` hook is configured
- Check `.variables.json` has the variable defined
- Verify jq is installed: `which jq`

### "Scout agents timing out"
- Reduce scale: `/scout "task" "2"` instead of "4"
- Check external CLI tools are installed (gemini, claude, etc.)
- Increase timeout in scout.md (default: 3 minutes)

### "Review keeps finding same issues"
- Check `.claude/.fix-attempts.txt` for count
- After 2 attempts, requires manual intervention
- Review `.review-report.md` for persistent issues

---

**System Status:** ✅ ACTIVE
**Last Updated:** 2025-10-09
**Version:** 1.0.0
