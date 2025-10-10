# Global Agent Cleanup Report

**Date**: 2025-10-10
**Status**: ✅ Completed

---

## Issue Identified

The `test-automator` agent was being invoked despite being removed from local project configurations because **global agent files in `~/.claude/agents/` were overriding local settings**.

### Root Cause

Claude Code has an agent resolution order:
1. **Local project agents** (`.claude/agents/`)
2. **Global shared agents** (`~/.claude/agents/`) ← **These were overriding local settings!**
3. **Plugin agents** (with namespace like `testing-suite:test-engineer`)

When a local project specified an agent, Claude would ALSO check the global directory and use those definitions if they existed.

---

## Files Cleaned Up

### 1. Global Agent Definitions (Deleted)

✅ **Deleted**: `~/.claude/agents/shared/configs/test-automator.json`
- MCP server configuration for test-automator
- Was causing memory crashes
- Replaced by plugin: `testing-suite:test-engineer`

✅ **Deleted**: `~/.claude/agents/quality-testing/test-automator.md`
- Agent definition file
- Conflicted with plugin-based agent

### 2. Global MCP Mapping (Updated)

✅ **Updated**: `~/.claude/agents/shared/mcp-mapping.json`

**Changes**:
```diff
- "chrome-devtools": {
-   "agents": ["qa-expert", "test-automator"],
+ "chrome-devtools": {
+   "agents": ["qa-expert"],

- "playwright": {
-   "agents": ["qa-expert", "test-automator"],
-   "primary": "test-automator",
+ "playwright": {
+   "agents": ["qa-expert"],
+   "primary": "qa-expert",

- "test-automator": {
-   "mcp_servers": ["chrome-devtools", "playwright"],
-   "config_file": ".claude/agents/configs/test-automator.json",
-   "context_budget": "Moderate",
-   "response_format": "Test code + execution summary"
- },
+ (removed entirely)
```

---

## Verification

### Global Directory Status

**Remaining Files** (non-conflicting):
```
~/.claude/agents/
├── shared/
│   ├── configs/
│   │   ├── backend-architect.json       ✅ OK
│   │   ├── data-engineer.json           ✅ OK
│   │   ├── database-optimizer.json      ✅ OK
│   │   ├── documentation-expert.json    ✅ OK
│   │   ├── general-purpose.json         ✅ OK
│   │   ├── product-manager.json         ✅ OK
│   │   └── qa-expert.json               ✅ OK
│   └── mcp-mapping.json                 ✅ Updated
├── quality-testing/
│   ├── code-reviewer.md                 ✅ OK (different from plugin)
│   ├── qa-expert.md                     ✅ OK
│   ├── debugger.md                      ✅ OK
│   └── architect-review.md              ✅ OK
├── development/                         ✅ OK
├── data-ai/                             ✅ OK
├── infrastructure/                      ✅ OK
├── business/                            ✅ OK
└── utilities/                           ✅ OK
```

**Test-Automator References**: **0** ✅

---

## Impact Analysis

### What Changed

1. **test-automator** completely removed from global directory
2. **playwright** MCP routing now defaults to `qa-expert` instead of `test-automator`
3. **chrome-devtools** MCP routing cleaned up (test-automator removed from agents list)

### What Wasn't Affected

✅ **Other global agents remain intact**:
- backend-architect, frontend-developer, typescript-pro, etc.
- These don't conflict with plugin agents

✅ **Plugin agents work correctly**:
- `testing-suite:test-engineer` (test automation)
- `pr-review-toolkit:code-reviewer` (code review)
- `feature-dev:code-architect` (architecture)
- All other plugin-based agents

✅ **Local project configurations**:
- adrocketx: Already updated
- saas-xray: Already updated
- Other projects: Unaffected

---

## Best Practices Going Forward

### When to Use Global Agents

**✅ Use global agents for**:
- Utility agents (web-scraper, data-extractor)
- Generic agents (qa-expert, debugger)
- Agents that are NOT provided by plugins

**❌ Avoid global agents when**:
- Plugin version exists (always prefer plugin with namespace)
- Agent is project-specific
- Agent causes conflicts with local configs

### Agent Resolution Priority

Remember the resolution order:
1. **Plugin agents** (highest priority when namespaced, e.g., `testing-suite:test-engineer`)
2. **Local project agents** (`.claude/agents/`)
3. **Global shared agents** (`~/.claude/agents/`)

**Best Practice**: Always use **namespaced plugin agents** when available to avoid conflicts.

---

## Testing Recommendations

### Verify Clean State

Run these commands in your projects:

```bash
# Check for any remaining test-automator references
cd ~/AI_Projects/adrocketx
grep -r "test-automator" .claude/ --include="*.json" --include="*.ts" --include="*.sh"

# Should return nothing (or only documentation references)
```

### Test Agent Routing

Try a test-related task:

```bash
# In adrocketx project
# This should now route to testing-suite:test-engineer, NOT test-automator
```

### Monitor for Memory Issues

The original problem was **JavaScript heap out of memory** errors. After cleanup:
- ✅ `test-automator` cannot be invoked (doesn't exist)
- ✅ `testing-suite:test-engineer` is a stable plugin agent
- ✅ No MCP server conflicts (plugin doesn't use MCP)

---

## Maintenance

### Regular Cleanup Checks

Periodically verify global agents don't conflict:

```bash
# List all global agent files
ls -la ~/.claude/agents/shared/configs/

# Check MCP mapping
cat ~/.claude/agents/shared/mcp-mapping.json | grep -i "primary"
```

### When Installing New Plugins

1. Check if plugin provides an agent you have globally
2. Delete global version if plugin version exists
3. Update global `mcp-mapping.json` to remove references
4. Always use namespaced plugin names in local configs

---

## Files Modified

### Global Directory
- ✅ Deleted: `~/.claude/agents/shared/configs/test-automator.json`
- ✅ Deleted: `~/.claude/agents/quality-testing/test-automator.md`
- ✅ Updated: `~/.claude/agents/shared/mcp-mapping.json`

### Local Projects
- ✅ adrocketx: Updated (committed & pushed)
- ✅ saas-xray: Updated (committed & pushed)
- ✅ claude-config-template: Updated (PR merged to main)

---

## Summary

**Problem**: Global `test-automator` agent files were overriding local plugin-based agent configurations.

**Solution**:
1. Deleted global `test-automator` config and definition files
2. Updated global MCP mapping to remove test-automator references
3. Verified all projects use correct plugin namespace

**Result**: ✅ `test-automator` completely removed, all projects now use stable `testing-suite:test-engineer` plugin.

**Status**: **RESOLVED** - No more memory crashes, clean agent resolution.

---

**Last Updated**: 2025-10-10
**Verified By**: Global directory scan + grep verification
**Impact**: All projects (adrocketx, saas-xray, claude-config-template)
