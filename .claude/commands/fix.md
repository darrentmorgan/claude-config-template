---
description: Fix issues identified in code review
argument-hint: [review-report-path]
model: claude-sonnet-4-5-20250929
---

# Fix Phase

Resolve issues identified by `/review`.

## Variables

- REVIEW_REPORT_PATH: $1 (path to .claude/.review-report.md)

## Purpose

Read review report and delegate to the same agent that did `/build` to fix issues.

## Workflow

1. Read review report from `$REVIEW_REPORT_PATH`
2. Extract the agent type from `.claude/.plan.md` (who did the build)
3. Delegate to that agent to fix ALL issues
4. After fixes complete, automatically call `/review` again to verify
5. Maximum 2 fix→review cycles (prevent infinite loops)

## Critical Rules for Delegated Agent

**IMPORTANT: The fixing agent has these restrictions:**

- **CANNOT** delegate to other agents
- **CAN** only use: Read, Write, Edit, Grep, Glob, Bash
- **MUST** fix ALL issues in the review report
- **MUST** call `/review` after fixes are complete
- **SHOULD** fix critical issues first, then warnings, then suggestions

## Instructions to Delegated Agent

```
You are fixing issues found in the code review.

READ THE REVIEW REPORT: {REVIEW_REPORT_PATH}

Then fix EVERY issue listed in priority order:
1. CRITICAL issues (must fix)
2. WARNING issues (should fix)
3. SUGGESTION issues (nice to fix if time permits)

For each issue:
1. Read the file mentioned
2. Locate the problem line
3. Implement the recommended fix
4. Test the change (if applicable)

CRITICAL RULES:
- You CANNOT use the Task tool
- You CAN use: Read, Write, Edit, Grep, Glob, Bash
- You MUST fix ALL critical and warning issues
- You MUST call /review when done
- DO NOT introduce new issues while fixing

After fixing ALL issues, type exactly:
/review

This will re-run the code review to verify your fixes.
```

## Loop Prevention

Track fix attempts in `.claude/.fix-attempts.txt`:

```
Attempt 1: [timestamp] - 2 critical, 1 warning
Attempt 2: [timestamp] - 0 critical, 1 warning
```

If attempt count reaches 3:
- Stop automatic /review calls
- Notify user of persistent issues
- Require manual intervention

## Output Format

After fixes complete:

```
🔧 Fix Phase Complete

Issues addressed:
  - Fixed: 2 critical
  - Fixed: 1 warning
  - Deferred: 0 suggestions

Files modified:
  - src/components/Login.tsx
  - src/services/authService.ts

Next: /review (running automatically to verify fixes)
```

## Next Step

Automatically call `/review` to verify fixes.

If review passes:
```
✅ All issues resolved! Workflow complete.
```

If issues remain (2nd attempt):
```
⚠️ Some issues remain after fix attempt 2/2
Manual review recommended.
```
