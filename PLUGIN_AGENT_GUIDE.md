# Plugin Agent Guide

## Understanding Plugin Agent Namespacing

### Storage Location

Plugin-installed agents are stored globally at:
```
~/.claude/plugins/marketplaces/<marketplace-name>/<plugin-name>/components/agents/
```

For example, the `testing-suite` plugin agents are at:
```
~/.claude/plugins/marketplaces/claude-code-templates/cli-tool/components/agents/development-tools/test-engineer.md
```

### Agent Namespacing

**IMPORTANT**: Plugin agents MUST be referenced with their full namespace.

#### Correct Usage ✅

```javascript
// In delegation-map.json
{
  "primary_agent": "testing-suite:test-engineer"  // ✅ With namespace
}

// In code
Task({
  subagent_type: "testing-suite:test-engineer",  // ✅ Full path
  prompt: "Generate unit tests"
})
```

#### Incorrect Usage ❌

```javascript
// In delegation-map.json
{
  "primary_agent": "test-engineer"  // ❌ Missing namespace
}

// In code
Task({
  subagent_type: "test-engineer",  // ❌ Won't be found
  prompt: "Generate unit tests"
})
```

### Available Plugin Agents

From the error message, these plugin agents are available:

#### testing-suite (from claude-code-templates)
- `testing-suite:test-engineer`

#### pr-review-toolkit (from claude-code-plugins)
- `pr-review-toolkit:code-reviewer`
- `pr-review-toolkit:code-simplifier`
- `pr-review-toolkit:comment-analyzer`
- `pr-review-toolkit:pr-test-analyzer`
- `pr-review-toolkit:silent-failure-hunter`
- `pr-review-toolkit:type-design-analyzer`

#### feature-dev (from claude-code-plugins)
- `feature-dev:code-architect`
- `feature-dev:code-explorer`
- `feature-dev:code-reviewer`

#### security-pro (from claude-code-plugins)
- `security-pro:security-auditor`
- `security-pro:penetration-tester`
- `security-pro:compliance-specialist`
- `security-pro:incident-responder`

#### ai-ml-toolkit (from claude-code-plugins)
- `ai-ml-toolkit:ai-engineer`
- `ai-ml-toolkit:ml-engineer`
- `ai-ml-toolkit:nlp-engineer`
- `ai-ml-toolkit:computer-vision-engineer`
- `ai-ml-toolkit:mlops-engineer`

#### nextjs-vercel-pro (from claude-code-plugins)
- `nextjs-vercel-pro:frontend-developer`
- `nextjs-vercel-pro:fullstack-developer`

#### supabase-toolkit (from claude-code-plugins)
- `supabase-toolkit:data-engineer`
- `supabase-toolkit:data-scientist`

#### git-workflow (from claude-code-plugins)
- `git-workflow:git-flow-manager`

#### devops-automation (from claude-code-plugins)
- `devops-automation:cloud-architect`

#### documentation-generator (from claude-code-plugins)
- `documentation-generator:technical-writer`
- `documentation-generator:docusaurus-expert`

#### performance-optimizer (from claude-code-plugins)
- `performance-optimizer:performance-engineer`
- `performance-optimizer:load-testing-specialist`

#### project-management-suite (from claude-code-plugins)
- `project-management-suite:product-strategist`
- `project-management-suite:business-analyst`

#### agent-sdk-dev (from claude-code-plugins)
- `agent-sdk-dev:agent-sdk-verifier-py`
- `agent-sdk-dev:agent-sdk-verifier-ts`

### Why Plugin Agents Aren't Visible Without Namespace

1. **Namespace Isolation**: Plugins use namespaces to avoid naming conflicts between different plugins
2. **Global vs Local**: Local agents (in `.claude/agents/`) don't need namespaces, but plugin agents always do
3. **Agent Resolution Order**:
   - First checks local `.claude/agents/` (no namespace)
   - Then checks global `~/.claude/agents/` (no namespace)
   - Finally checks plugins with namespace `<plugin>:<agent>`

### Updating Your Configuration

#### Step 1: Update delegation-map.json

**OLD (Incorrect):**
```json
{
  "name": "Test Files",
  "pattern": "**/*.{test,spec}.{ts,tsx}",
  "primary_agent": "test-engineer",  // ❌
  "secondary_agents": ["code-reviewer-pro"],
  "triggers": ["Edit", "Write"]
}
```

**NEW (Correct):**
```json
{
  "name": "Test Files",
  "pattern": "**/*.{test,spec}.{ts,tsx}",
  "primary_agent": "testing-suite:test-engineer",  // ✅
  "secondary_agents": ["code-reviewer-pro"],
  "triggers": ["Edit", "Write"]
}
```

#### Step 2: Update delegation-router.ts

**OLD (Incorrect):**
```typescript
const fileTypeKeywords = [
  { keywords: ['test', 'spec', 'e2e'], agent: 'test-engineer' }, // ❌
];
```

**NEW (Correct):**
```typescript
const fileTypeKeywords = [
  { keywords: ['test', 'spec', 'e2e'], agent: 'testing-suite:test-engineer' }, // ✅
];
```

#### Step 3: Update agent_capabilities

**OLD (Incorrect):**
```json
{
  "agent_capabilities": {
    "test-engineer": {  // ❌
      "description": "Test code generation and strategy (plugin:testing-suite)",
      "plugin": "testing-suite@claude-code-templates"
    }
  }
}
```

**NEW (Correct):**
```json
{
  "agent_capabilities": {
    "testing-suite:test-engineer": {  // ✅
      "description": "Test code generation and strategy (plugin:testing-suite)",
      "plugin": "testing-suite@claude-code-templates"
    }
  }
}
```

### Testing Agent Discovery

Run this command to verify agents are accessible:
```bash
# List all available agents
claude agents list

# Or try invoking the agent directly
claude "Use testing-suite:test-engineer to generate tests for src/example.ts"
```

### Common Issues

#### Issue 1: "Agent type 'test-engineer' not found"
**Cause**: Missing namespace
**Solution**: Use `testing-suite:test-engineer` instead

#### Issue 2: Agents not showing up in /agents list
**Cause**: Plugins not installed or marketplace not synced
**Solution**:
```bash
# Re-sync marketplaces
claude /plugins sync

# Check installed plugins
claude /plugins list
```

#### Issue 3: Different projects see different agents
**Cause**: Project-specific plugin configurations in `.mcp.json`
**Solution**: Ensure consistent plugin installation across projects

### Best Practices

1. **Always use full namespace** for plugin agents in configuration files
2. **Document plugin dependencies** in README or setup scripts
3. **Use local agents** for project-specific custom agents (no namespace needed)
4. **Test after updates** to ensure agent discovery works
5. **Keep plugins synced** across team members

### Migration Checklist

When migrating from local agents to plugin agents:

- [ ] Update `delegation-map.json` with full namespaces
- [ ] Update `mcp-mapping.json` with full namespaces
- [ ] Update `scripts/delegation-router.ts` keyword mappings
- [ ] Update documentation references
- [ ] Test agent invocation
- [ ] Commit changes to version control
- [ ] Notify team members to sync plugins

---

**Last Updated**: 2025-10-10
**Related**: MIGRATION_NOTES.md (test-automator → test-engineer migration)
