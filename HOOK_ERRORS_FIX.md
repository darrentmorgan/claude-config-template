# Hook Errors Fix

## Phase 2: Path Resolution Issue - October 11, 2025

### Problem Summary

All three projects (`claude-config-template`, `adrocketx`, `saas-xray`) were experiencing intermittent hook execution failures with "No such file or directory" error 127:
- `PreToolUse:Bash [.claude/hooks/tool.bash.block.sh "$COMMAND"] failed with status code 127`
- `PostToolUse:Edit [.claude/hooks/tool-use.sh "$FILE_PATH"] failed with status code 127`
- All other hooks with relative paths

### Root Cause

**Relative paths in hook configurations** - The hooks were configured with relative paths like `.claude/hooks/script.sh` instead of using the `$CLAUDE_PROJECT_DIR` environment variable.

**Why this fails**: When Claude Code's working directory is not the project root (e.g., during agent execution or different startup contexts), relative paths cannot be resolved, resulting in error 127 "command not found".

### Solution Applied

Updated ALL hook configurations to use `$CLAUDE_PROJECT_DIR` environment variable:

**Before (WRONG)**:
```json
"command": ".claude/hooks/tool.bash.block.sh \"$COMMAND\""
```

**After (CORRECT)**:
```json
"command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/tool.bash.block.sh \"$COMMAND\""
```

### Files Fixed

**claude-config-template**:
- `.claude/settings.local.json` - Updated all 6 hook paths
- `settings.local.json` - Updated hook paths
- `.claude/hooks/README.md` - Added path resolution guidance

**saas-xray**:
- `.claude/settings.local.json` - Updated all 6 hook paths

**adrocketx**:
- `.claude/settings.local.json` - Updated all 6 hook paths

### Result

✅ Hooks now work consistently regardless of working directory
✅ No more error 127 "No such file or directory" failures
✅ Auto-formatting, type checking, and bash blocking now function properly
✅ Template documentation updated with correct patterns

---

## Phase 1: Missing Files Issue - October 10, 2025

### Problem Summary

Both `adrocketx` and `saas-xray` projects were experiencing hook execution failures with "No such file or directory" errors for:
- `.claude/hooks/agent-depth-guard.sh`
- `.claude/hooks/agent-stack-manager.sh`
- `.claude/hooks/delegation-logger.sh`

### Root Cause

1. **Experimental Task hooks configured but files missing**:
   - `adrocketx` had `PreToolUse:Task` and `PostToolUse:Task` hooks configured in `.claude/settings.local.json`
   - These hooks referenced scripts that were created in an experimental session but never properly deployed
   - The hook scripts existed in backups but were not in the active projects

2. **saas-xray broken symlink**:
   - `.claude/agents/configs` was a symlink pointing to `~/.claude/agents/shared/configs`
   - This global directory was deleted during the global-to-local settings migration
   - The broken symlink prevented Claude Code from loading ANY agent configurations

## Solution Applied

### Phase 1: Fixed saas-xray Agent Configuration
✅ **Removed broken symlink**: Deleted `.claude/agents/configs` symlink
✅ **Created proper configs directory**: Copied all 20+ agent configs from template
✅ **Updated settings**: Synced `.claude/settings.local.json` with template

### Phase 2: Removed Experimental Task Hooks
✅ **Cleaned adrocketx hooks**: Removed `PreToolUse:Task` and `PostToolUse:Task` configurations
✅ **Cleaned saas-xray hooks**: Ensured no Task hooks present
✅ **Replaced with template hooks**: Used stable `PreToolUse:Bash` hooks from template

### Phase 3: Synced Hook Files
✅ **Copied missing hooks to both projects**:
- `tool.bash.block.sh` - Bash command validation
- `post-git-push.sh` - Post-push automation
- `user-prompt-submit.sh` - Pre-request processing
- `plugin-router.sh` - Plugin routing

## Files Changed

### adrocketx
```
Modified:
  .claude/settings.local.json         (removed Task hooks)

Added:
  .claude/hooks/plugin-router.sh
  .claude/hooks/post-git-push.sh
  .claude/hooks/tool.bash.block.sh
  .claude/hooks/user-prompt-submit.sh
```

### saas-xray
```
Deleted:
  .claude/agents/configs              (broken symlink)

Added:
  .claude/agents/configs/             (20+ agent configs)
  .claude/hooks/plugin-router.sh
  .claude/hooks/post-git-push.sh
  .claude/hooks/tool.bash.block.sh
  .claude/hooks/user-prompt-submit.sh

Modified:
  .claude/settings.local.json         (updated permissions & hooks)
```

## Hook Configuration Now (Both Projects)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "command": ".claude/hooks/tool.bash.block.sh \"$COMMAND\"",
          "blockOnFailure": true
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{
          "command": ".claude/hooks/tool-use.sh \"$FILE_PATH\""
        }]
      },
      {
        "matcher": "Write",
        "hooks": [{
          "command": ".claude/hooks/tool-use.sh \"$FILE_PATH\""
        }]
      },
      {
        "matcher": "Bash(git push:*)",
        "hooks": [{
          "command": ".claude/hooks/post-git-push.sh"
        }]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          { "command": ".claude/hooks/user-prompt-submit.sh \"$USER_MESSAGE\"" },
          { "command": ".claude/hooks/pre-request-router.sh \"$USER_MESSAGE\"" },
          { "command": ".claude/hooks/plugin-router.sh \"$USER_MESSAGE\"" }
        ]
      }
    ]
  }
}
```

## Why Task Hooks Were Removed

The `PreToolUse:Task` and `PostToolUse:Task` hooks were experimental features designed to:
- Track agent delegation depth (prevent infinite recursion)
- Maintain agent call stack
- Log delegation history

**However:**
- They were never fully implemented or tested
- The scripts existed only in backups, not in production
- The template works perfectly without them
- They added complexity without proven benefit
- Delegation works fine using Claude Code's built-in Task tool

### Verification (Phase 1)

After applying Phase 1 fixes:

✅ **saas-xray**: Can now load agent configurations
✅ **adrocketx**: No more missing file errors
✅ **Both projects**: All hooks reference existing, working scripts
✅ **Template**: Remains the source of truth for hook configurations

## Prevention Guidelines

To prevent hook issues in the future:

### Path Configuration
1. **ALWAYS use `$CLAUDE_PROJECT_DIR` for hook paths**
   - ✅ `"$CLAUDE_PROJECT_DIR"/.claude/hooks/script.sh`
   - ❌ `.claude/hooks/script.sh`

2. **Why absolute paths matter**:
   - Claude Code's working directory may change during execution
   - Agents may execute from different contexts
   - Relative paths only work when CWD is project root

### General Best Practices
3. **Never add hook configurations without verifying the scripts exist**
4. **Always sync hooks from template, don't create experimental ones**
5. **Test hooks after migration or major changes**
6. **Keep hook scripts in template for easy distribution**
7. **Document any new hooks before deploying**

## Related Documentation

- [Hook Configuration Guide](/.claude/hooks/README.md)
- [Global vs Local Settings](/.claude/docs/GLOBAL_VS_LOCAL_SETTINGS.md)
- [Migration Summary](/MIGRATION_SUMMARY.md)
- [Template Sync Script](/scripts/sync-from-template.sh)

---

**Status**: ✅ Fixed (Both Phase 1 and Phase 2)
**Latest Update**: October 11, 2025
**Impact**: All projects now have reliable hook execution with no errors
