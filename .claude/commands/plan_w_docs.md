---
description: Plan the task based on discovered files with documentation
argument-hint: [user-prompt] [documentation-urls] [relevant_files_collection_path]
model: claude-sonnet-4-5-20250929
---

# Plan Phase (with Documentation)

Create an implementation plan based on the files discovered by `/scout` and provided documentation.

## Variables

- USER_PROMPT: $1
- DOCUMENTATION_URLS: $2
- RELEVANT_FILES_COLLECTION_PATH: $3 (path to scout results file)

## Purpose

Read the discovered files (at specific line ranges) and create a detailed implementation plan.

## Workflow

1. Read the scout results from `$RELEVANT_FILES_COLLECTION_PATH`
2. For each file in the results:
   - Use Read tool with offset/limit parameters from scout output
   - Example: If scout returned `src/Login.tsx (offset: 45, limit: 30)`, read lines 45-75 only
3. Fetch and review documentation from `$DOCUMENTATION_URLS` (if provided)
4. Analyze the existing code architecture and patterns
5. Create a step-by-step implementation plan

## Critical Rules

- DO NOT use Task tool
- DO NOT delegate to other agents
- ONLY use Read tool to read files (use offset/limit parameters)
- ONLY use WebFetch tool to read documentation URLs
- Read ONLY the line ranges specified in scout results (not entire files)
- Output plan in structured markdown format

## Plan Format

Create `.claude/.plan.md` with this structure:

```markdown
# Implementation Plan

## Task
[Original user prompt]

## Files to Modify

### File: src/components/Login.tsx
**Lines:** 45-75 (existing code analyzed)
**Changes:**
1. Add authentication state management
2. Integrate with authService
3. Add error handling

**Estimated Impact:** Medium

### File: src/services/authService.ts
**Lines:** 1-50 (existing code analyzed)
**Changes:**
1. Add login method
2. Add token management
3. Export auth state

**Estimated Impact:** High

## Implementation Order

1. Update authService.ts first (foundation)
2. Modify Login.tsx to use new service
3. Add error boundaries
4. Update tests

## Architecture Notes

- Using existing React Context pattern
- Following current TypeScript conventions
- Maintaining backward compatibility

## Documentation References

- [Link 1]: Authentication best practices
- [Link 2]: API integration guide

## Estimated Complexity

Medium - 2-3 files, ~100 lines of code

## Next Agent

Recommended agent for /build: **frontend-developer**
(Based on file types: .tsx, .ts)
```

## Instructions

- We're executing a three step engineering workflow to deliver on the `USER_PROMPT`.
- Execute each step in order, top to bottom.
- If you're returned an unexpected result, stop and notify the user.
- Place each argument for the SlashCommands arguments within double quotes and convert any nested double quotes to single quotes.
- Do not alter the `USER_PROMPT` variable in anyway, pass it in as is.
- IMPORTANT: Flow through each step in the workflow in order, top to bottom. Only waiting for the previous step to complete before starting the next step. Do not stop in between steps. Complete every step in the workflow before stopping.

## Output

Save plan to `.claude/.plan.md` and display summary:

```
📋 Plan Complete

Files to modify: 3
Complexity: Medium
Recommended agent: frontend-developer

Next: Run /build to implement the plan
```

## Next Step

After plan completes, the system will automatically suggest:
```
📋 Plan complete. Run /build to implement
```
