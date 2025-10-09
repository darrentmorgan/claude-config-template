---
description: Build the task based on the implementation plan
argument-hint: [path_to_plan]
model: claude-sonnet-4-5-20250929
---

# Build Phase

Execute the implementation plan created by `/plan_w_docs`.

## Variables

- PLAN_PATH: $1 (path to .claude/.plan.md)

## Purpose

Read the plan and delegate to the appropriate specialized agent to implement the changes.

## Workflow

1. Read the plan from `$PLAN_PATH`
2. Identify the recommended agent from the plan (e.g., "frontend-developer", "backend-architect")
3. Delegate to that agent ONCE using Task tool
4. The agent will:
   - Read the plan
   - Implement all changes listed
   - Follow the implementation order specified
   - Create or modify files as needed
5. When agent completes, it MUST call `/review` to validate changes

## Critical Rules for the Delegated Agent

**IMPORTANT: The agent you delegate to has these restrictions:**

- **CANNOT** delegate to other agents (Task tool blocked)
- **CAN** only use: Read, Write, Edit, Grep, Glob, Bash (for git, npm, etc.)
- **MUST** implement ALL changes in the plan before finishing
- **MUST** call `/review` slash command when done (the ONLY slash command allowed)
- **CANNOT** stop midway - must complete entire plan

## Agent Selection Logic

Based on file types in the plan:

- **frontend-developer**: .tsx, .jsx, .vue, .css, frontend/
- **backend-architect**: server/, api/, .sql, database/, backend/
- **typescript-pro**: Complex type work, .d.ts, type refactoring
- **test-automator**: .test.ts, .spec.ts, testing work
- **python-pro**: .py, Python-specific work

If multiple types, choose the agent for the PRIMARY changes.

## Instructions to Delegated Agent

When delegating via Task tool, include this exact prompt:

```
You are implementing the plan in {PLAN_PATH}.

READ THE ENTIRE PLAN FIRST using the Read tool.

Then implement EVERY change listed in the Implementation Order section.

CRITICAL RULES:
- You CANNOT use the Task tool (blocked)
- You CAN use: Read, Write, Edit, Grep, Glob, Bash
- You MUST implement ALL changes before stopping
- You MUST call /review when done (type exactly: /review)
- DO NOT stop midway through the plan
- Follow the implementation order exactly as specified

After completing ALL changes, type exactly:
/review

This will trigger the quality gate to validate your work.
```

## Output Format

After delegation completes:

```
🔨 Build Phase Complete

Agent used: frontend-developer
Files modified: 3
  - src/components/Login.tsx
  - src/services/authService.ts
  - src/hooks/useAuth.ts

Next: /review (should be called automatically by agent)
```

## Next Step

The delegated agent will automatically call `/review` when done.
