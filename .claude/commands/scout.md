---
description: Search the codebase for files needed to complete the task
argument-hint: [user-prompt] [scale]
model: claude-sonnet-4-5-20250929
---

# Scout Phase

Search the codebase for files needed to complete the task using parallel fast agents.

## Variables

- USER_PROMPT: $1
- SCALE: $2 (optional, defaults to 3)

## Purpose

Search the codebase for files needed to complete the task using a fast, token-efficient agent.

First we scout the codebase for files needed to complete the task.
Then we plan the task based on the files found.
Then we build the task based on the plan.

## Workflow

- Write a prompt for `$SCALE` number of agents to the Task tool that will immediately call the Bash tool to run these commands to kick off your agents to conduct the search:
  - `gemini -p "[prompt]" --model gemini-2.5-flash-preview-09-2025`
  - `opencode run [prompt] --model cerebras/qwen-3-coder-480b` (if count >= 2)
  - `gemini -p "[prompt]" --model gemini-2.5-flash-lite-preview-09-2025` (if count >= 3)
  - `codex exec -m gpt-5-codex -s read-only -c model_reasoning_effort="low" "[prompt]"` (if count >= 4)
  - `claude -p "[prompt]" --model haiku` (if count >= 5)

- How to prompt the agents:
  - IMPORTANT: Kick these agents off in parallel using the Task tool.
  - IMPORTANT: These agents are calling OTHER agentic coding tools to search the codebase. DO NOT call any search tools yourself.
  - IMPORTANT: That means with the Task tool, you'll immediately call the Bash tool to run the respective agentic coding tool (gemini, opencode, claude, etc.)
  - IMPORTANT: Instruct the agents to quickly search the codebase for files needed to complete the task. This isn't about a full blown search, just a quick search to find the files needed to complete the task.
  - Instruct the subagent to use a timeout of 3 minutes for each agent's bash call. Skip any agents that don't return within the timeout, don't restart them.
  - Make it absolutely clear that the Task tool is ONLY going to call the Bash tool and pass in the appropriate prompt, replacing the [prompt] with the actual prompt you want to run.
  - Make it absolutely clear the agent is NOT implementing the task, the agent is ONLY searching the codebase for files needed to complete the task.
  - Prompt the agent to return a structured list of files with specific line ranges in this format:
    - `- <path to file> (offset: N, limit: M)` where offset is the starting line number and limit is the number of lines to read
    - If there are multiple relevant sections in the same file, repeat the entry with different offset/limit values
  - Execute additional agent calls in round robin fashion.
  - Give them the relevant information needed to complete the task.

## Instructions

- We're executing a three step engineering workflow to deliver on the `USER_PROMPT`.
- Execute each step in order, top to bottom.
- If you're returned an unexpected result, stop and notify the user.
- Place each argument for the SlashCommands arguments within double quotes and convert any nested double quotes to single quotes.
- Do not alter the `USER_PROMPT` variable in anyway, pass it in as is.
- IMPORTANT: Flow through each step in the workflow in order, top to bottom. Only waiting for the previous step to complete before starting the next step. Do not stop in between steps. Complete every step in the workflow before stopping.

## Output Format

After all agents complete (or timeout), merge and deduplicate results. Save to `.claude/.scout-results.txt` in this format:

```
# Scout Results for: [task description]
# Generated: [timestamp]

## Files Found

- src/components/Login.tsx (offset: 45, limit: 30)
- src/hooks/useAuth.ts (offset: 12, limit: 50)
- src/services/authService.ts (offset: 1, limit: 100)

## Search Summary

- Total agents: 3
- Successful: 2
- Timed out: 1
- Unique files: 3
- Total sections: 3
```

## Next Step

After scout completes, the system will automatically suggest:
```
📁 Scout complete. Run /plan to create implementation plan
```
