---
description: Run a three step engineering workflow to deliver on the `USER_PROMPT`
argument-hint: [user-prompt] [documentation-urls]
model: claude-sonnet-4-5-20250929
---

# Scout Plan Build

## Purpose

Run a three step engineering workflow to deliver on the `USER_PROMPT`.

First we scout the codebase for files needed to complete the task.
Then we plan the task based on the files found.
Then we build the task based on the plan.

## Variables

USER_PROMPT: $1
DOCUMENTATION_URLS: $2

## Workflow

> Run the workflow in order, top to bottom. Do not stop in between steps. Complete every step in the workflow before stopping.

1. Run SlashCommand(`/scout "[USER_PROMPT]" "4"`) -> `relevant_files_collection_path`
2. Run SlashCommand(`/plan_w_docs "[USER_PROMPT]" "[DOCUMENTATION_URLS]" "[relevant_files_collection_path]"`) -> `path_to_plan`
3. Run SlashCommand(`/build "[path_to_plan]"`) -> `build_report`
4. Finally, report the work done based on the `Report` section.

## Instructions

- We're executing a three step engineering workflow to deliver on the `USER_PROMPT`.
- Execute each step in order, top to bottom.
- If you're returned an unexpected result, stop and notify the user.
- Place each argument for the SlashCommands arguments within double quotes and convert any nested double quotes to single quotes.
- Do not alter the `USER_PROMPT` variable in anyway, pass it in as is.
- IMPORTANT: Flow through each step in the workflow in order, top to bottom. Only waiting for the previous step to complete before starting the next step. Do not stop in between steps. Complete every step in the workflow before stopping.

## Report

After workflow completes successfully:

```markdown
# Workflow Complete 🎉

## Task
{USER_PROMPT}

## Steps Executed

### 1. Scout ✅
- Files found: {count}
- Agents used: {number}
- Time: {duration}

### 2. Plan ✅
- Files to modify: {count}
- Complexity: {level}
- Agent selected: {agent_type}

### 3. Build ✅
- Files modified: {list}
- Changes made: {summary}

### 4. Review ✅
- Status: {PASS/FAIL}
- Issues: {count}

## Files Modified

{list of modified files with summaries}

## Next Steps

{any follow-up actions or recommendations}
```

## Error Handling

If any step fails:

1. **Scout fails**: Report which agents timed out, suggest manual file specification
2. **Plan fails**: Report missing information, suggest documentation or context
3. **Build fails**: Report errors from agent, suggest `/fix` or manual intervention
4. **Review fails**: Report issues found, automatically trigger `/fix`

## State Tracking

Save workflow state to `.claude/.workflow-state.json`:

```json
{
  "task": "USER_PROMPT",
  "started_at": "timestamp",
  "current_step": "build",
  "completed_steps": ["scout", "plan"],
  "scout_results": "path/to/results",
  "plan_path": "path/to/plan",
  "status": "in_progress"
}
```

This allows resuming if interrupted.
