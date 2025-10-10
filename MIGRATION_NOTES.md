# Migration Notes

## test-automator → test-engineer (2025-10-10)

### Reason for Change

The `test-automator` agent was causing heap memory crashes due to excessive context usage when handling test generation tasks. The agent has been replaced with `test-engineer`, a more stable plugin-based agent from the `testing-suite@claude-code-templates` plugin.

### Impact

**Memory Stability**: The new `test-engineer` agent prevents the JavaScript heap out of memory errors that were occurring with `test-automator`.

**Functionality**: Test generation capabilities remain the same - unit tests, integration tests, E2E tests, and test coverage analysis are all still available.

**MCP Servers**: Unlike `test-automator`, the `test-engineer` agent does not require direct MCP server access (chrome-devtools, playwright). It operates as a plugin-based agent for improved stability.

### Changes Made

#### Configuration Files
- ✅ `.claude/agents/delegation-map.json` - Updated all 9 references
- ✅ `agents/mcp-mapping.json` - Removed test-engineer from MCP server lists
- ✅ `scripts/delegation-router.ts` - Updated keyword routing (2 locations)
- ✅ `agents/configs/test-automator.json` - Deleted (no longer needed)

#### Documentation Files
- ✅ `docs/AGENT_REFERENCE.md` - Updated agent section and quality gates
- ✅ `README.md` - Updated file routing example
- ✅ `INSTALLATION.md` - Updated agent config examples (3 locations)
- ✅ `CLAUDE_MD_QUICKSTART.md` - Updated agent table
- ✅ `docs/CLAUDE_MD_CONDENSED.md` - Updated Pre-Action Checklist and Quick Reference (2 locations)
- ✅ `docs/DELEGATION.md` - Updated delegation rules (2 locations)
- ✅ `docs/WORKFLOWS.md` - Updated agent delegation examples (2 locations)

### Usage

No changes to user workflow are required. The agent routing automatically detects test-related keywords and routes to `test-engineer` instead:

**Before:**
```
User: "Generate tests for the auth service"
→ Routed to: test-automator (chrome-devtools, playwright)
```

**After:**
```
User: "Generate tests for the auth service"
→ Routed to: test-engineer (plugin:testing-suite)
```

### Remaining References

There are still ~140 references to `test-automator` in example documentation, implementation guides, and test results. These are non-functional and can be updated over time as needed.

### Rollback

If you need to rollback to `test-automator` for any reason:

```bash
# 1. Restore the deleted config (from git history)
git show HEAD~1:agents/configs/test-automator.json > agents/configs/test-automator.json

# 2. Revert all changes
git revert <commit-hash>

# 3. Or manually replace all instances of "test-engineer" with "test-automator"
```

**Note**: Rollback is not recommended due to memory stability issues.

### Future Considerations

The `testing-suite` plugin provides additional capabilities beyond the old `test-automator`:
- Better test strategy planning
- Improved coverage analysis
- Integration with CI/CD systems
- Test quality metrics

Consider exploring these features as you work with the new agent.

---

**Migration Date**: 2025-10-10
**Completed By**: Automated PR review and update process
**Related PR**: #1 (feat: add plugin router hook to pre-user-prompt-submit)
