# Troubleshooting Guide

## Memory Issues

### JavaScript Heap Out of Memory

**Symptoms:**
```
FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
```

**Root Cause:**
Long conversations accumulate context (conversation history + file reads/writes), eventually reaching Node.js heap limit.

**Context Usage Indicators:**
- Status line shows: `🧠 141,656 (71%)` - approaching limit
- Crashes typically occur above 70% context usage
- Each file read, tool use, and response adds to context

**Solutions:**

#### 1. Start Fresh Conversation (Immediate Fix)
- Start a new Claude Code session
- Previous work is saved in git
- Context resets to 0%

#### 2. Use Modular Documentation (Reduces Base Context)
```bash
# Install condensed CLAUDE.md
bash scripts/update-claude-md.sh
```

Benefits:
- Reduces CLAUDE.md from 800+ lines to ~290 lines
- Detailed docs loaded on-demand only
- Saves ~40k tokens per conversation

#### 3. Delegate Early and Often (Prevents Accumulation)
```bash
# Bad: Read 20 files yourself
# Good: Delegate to specialized agent
Task(frontend-developer, "Review all React components")
```

Agent delegation:
- Sub-agents work in isolated context
- Only return summaries (not full file contents)
- Main context stays lean

#### 4. Increase Node.js Heap (Temporary Workaround)
```bash
# In your shell profile (~/.zshrc or ~/.bashrc)
export NODE_OPTIONS="--max-old-space-size=8192"
```

Increases heap from 4GB to 8GB. Not a permanent solution.

---

## Context Usage Best Practices

### Monitor Context Usage
Watch the status line:
- 🟢 0-40%: Healthy
- 🟡 40-60%: Monitor
- 🟠 60-70%: Delegate more
- 🔴 70%+: Risk of crash, start new session

### Reduce Context in Long Sessions

**1. Delegate Complex Tasks**
```bash
# Instead of reading/editing many files:
Task(general-purpose, "Refactor all components to use new hook")
```

**2. Use Grep Instead of Read for Searches**
```bash
# Bad: Read 10 files to find function
# Good: Grep for function name
Grep("function myFunction", "src/**/*.ts")
```

**3. Avoid Repeated File Reads**
- Cache information in todos/notes
- Don't re-read files unnecessarily

**4. Use Scout → Plan → Build**
```bash
/scout Find files for dark mode feature
# Review scout-report.md
/plan Create implementation plan
# Review plan.md
/build Execute plan
```

Scout minimizes context by identifying only essential files.

---

## Delegation System Issues

### Agent Not Loading MCP Server

**Symptoms:**
Agent can't access Supabase/Stripe/etc.

**Check:**
```bash
# Verify agent has MCP server configured
cat .claude/agents/configs/backend-architect.json | jq '.mcpServers'
```

**Fix:**
Ensure MCP server is defined in agent config:
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase"],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "{{TOKEN}}"
      }
    }
  }
}
```

### Pre-Request Hook Not Triggering

**Symptoms:**
No delegation suggestions appear

**Check:**
```bash
# Verify hook is executable
ls -lh .claude/hooks/pre-request-router.sh

# Test manually
.claude/hooks/pre-request-router.sh "Create Button component"
```

**Fix:**
```bash
chmod +x .claude/hooks/pre-request-router.sh
```

### Delegation Router Not Found

**Symptoms:**
```
delegation-router.ts not found
```

**Fix:**
```bash
# Verify script exists
ls .claude/scripts/delegation-router.ts

# Re-run setup if missing
npx degit darrentmorgan/claude-config-template .claude-temp --force
cd .claude-temp && bash setup.sh && cd .. && rm -rf .claude-temp
```

---

## Modular Documentation Issues

### Files Not Loading On-Demand

**Symptoms:**
Claude says "I don't have information about X"

**Check:**
```bash
# Verify docs exist
ls .claude/docs/
```

**Fix:**
Ensure CLAUDE.md has correct file references:
```markdown
**Full Delegation Protocol**: Read `.claude/docs/DELEGATION.md`
```

Claude will read the file when needed.

---

## Workflow Issues

### /scout Command Not Found

**Symptoms:**
```
Unknown command: /scout
```

**Fix:**
```bash
# Verify slash commands exist
ls .claude/commands/workflows/

# Re-run setup if missing
bash setup.sh
```

### Scout Report Empty

**Symptoms:**
scout-report.md has no files listed

**Possible Causes:**
1. Project structure doesn't match default scan paths
2. No matching files found

**Fix:**
Edit `.claude/commands/workflows/scout.md` to match your project:
```markdown
Default scan locations:
- app/ (change to your app directory)
- src/components/ (change to your components path)
```

---

## Performance Issues

### Slow Agent Response Times

**Causes:**
1. MCP server startup time
2. Large file reads
3. Network latency (web searches/fetches)

**Solutions:**

**1. Use Lightweight Agents for Simple Tasks**
```bash
# Use haiku-based agents for simple operations
Task(task-coordinator, "Create ClickUp task")  # Fast (haiku)
# vs
Task(product-manager, "Create roadmap")  # Slower (sonnet)
```

**2. Parallel Execution**
```bash
# Run independent tasks in parallel
Task(frontend-developer, "Create component") +
Task(test-automator, "Create tests") +
Task(code-reviewer-pro, "Review code")
```

**3. Minimize File Reads in Hooks**
Edit `.claude/hooks/tool-use.sh` to skip expensive checks:
```bash
# Disable type checking if slow
# $PKG_MANAGER exec tsc --noEmit "$MODIFIED_FILE"
```

---

## Installation Issues

### setup.sh Fails with Permission Denied

**Fix:**
```bash
chmod +x setup.sh
bash setup.sh
```

### Hooks Not Executing

**Check:**
```bash
# Verify hooks are executable
ls -lh .claude/hooks/*.sh

# Check permissions in settings
cat .claude/settings.local.json | jq '.hooks'
```

**Fix:**
```bash
chmod +x .claude/hooks/*.sh
```

---

## Git Issues

### Massive Context Exhaustion Error

**Symptoms:**
Git operations fail due to context usage

**Cause:**
Long conversation + git operations accumulate context

**Solution:**
Start new session, previous work is saved:
```bash
git status  # Work is still there
git log     # Commits are preserved
```

---

## FAQ

**Q: Why does context keep growing?**
A: Every message, file read, and tool use adds to context. This is expected behavior.

**Q: Can I clear context without restarting?**
A: No, start a new Claude Code session. Your work is saved in git.

**Q: How do I know if I'm using too much context?**
A: Watch status line. Above 60% = delegate more. Above 70% = risk of crash.

**Q: Does delegation reduce context?**
A: Yes! Sub-agents work in isolated context and return only summaries.

**Q: Should I use modular docs?**
A: Yes! Reduces CLAUDE.md from 800+ to ~290 lines, saving ~40k tokens.

**Q: What's the best way to avoid memory crashes?**
A:
1. Use modular documentation (reduces base context)
2. Delegate complex tasks early
3. Monitor context usage
4. Start new session above 70%

---

## Reporting Issues

If you encounter issues not covered here:

1. Check context usage in status line
2. Review logs: `.claude/.tool-use.log`, `.claude/.session.log`
3. Create issue: https://github.com/darrentmorgan/claude-config-template/issues

Include:
- Context usage percentage
- Error message
- Steps to reproduce
- Relevant log entries
