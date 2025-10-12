#!/usr/bin/env tsx
/**
 * Delegation Router with Artifact System Integration
 *
 * Programmatically matches user requests to specialized agents based on:
 * 1. File pattern matching (delegation_rules)
 * 2. Keyword matching (mcp_routing_rules)
 *
 * Integrated with artifact system for:
 * - Session initialization and tracking
 * - Agent registration and scratchpad creation
 * - Artifact-enhanced prompts for agents
 * - Response processing with summary extraction
 *
 * Usage:
 *   npx tsx .claude/scripts/delegation-router.ts "Create migration for users"
 *   # Output: backend-architect
 *
 *   npx tsx .claude/scripts/delegation-router.ts "Add button component" --execute
 *   # Executes delegation with artifact tracking
 *
 *   npx tsx .claude/scripts/delegation-router.ts "What's the weather?"
 *   # Output: none
 */

import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { minimatch } from 'minimatch';
import {
  initSession,
  registerAgent,
  appendToScratchpad,
} from './artifact-write.js';
import { getAllAgentSummaries } from './artifact-read.js';

const ARTIFACTS_DIR = join(process.cwd(), '.claude/artifacts');
const CURRENT_SESSION_FILE = join(ARTIFACTS_DIR, '.current-session');
const AGENTS_DIR = join(process.cwd(), '.claude/agents/configs');

interface DelegationRule {
  name: string;
  pattern: string;
  exclude?: string[];
  primary_agent: string;
  secondary_agents?: string[];
  triggers?: string[];
  context?: Record<string, unknown>;
}

interface MCPRoute {
  name: string;
  mcp_server: string;
  primary_agent: string;
  fallback_agent?: string;
  secondary_agents?: string[];
  keywords: string[];
  example_queries?: string[];
  special_instructions?: string;
}

interface DelegationMap {
  delegation_rules: DelegationRule[];
  agent_capabilities: Record<string, unknown>;
  execution_strategy: Record<string, unknown>;
  quality_gates: Record<string, unknown>;
  mcp_routing_rules: {
    description: string;
    main_orchestrator_policy: string;
    context_savings: string;
    routing_map: MCPRoute[];
    delegation_workflow: Record<string, string>;
    anti_patterns: string[];
    best_practices: string[];
  };
}

interface AgentConfig {
  agentName: string;
  description: string;
  mcpServers?: Record<string, unknown>;
  capabilities: string[];
  response_format?: Record<string, unknown>;
  routing_triggers?: string[];
  special_instructions?: string[];
  artifacts?: {
    enabled: boolean;
    scratchpad: boolean;
    auto_summary: boolean;
    detail_threshold: number;
    instructions?: string;
  };
}

/**
 * Safely load and validate JSON file with error handling
 */
function loadJsonFile<T>(filePath: string, fileDescription: string): T {
  try {
    if (!existsSync(filePath)) {
      throw new Error(`File not found: ${filePath}`);
    }
    const content = readFileSync(filePath, 'utf-8');
    return JSON.parse(content) as T;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`Error loading ${fileDescription}: ${errorMessage}`);
    console.error(`Path: ${filePath}`);
    process.exit(1);
  }
}

/**
 * Load delegation map from .claude/agents/delegation-map.json
 */
function loadDelegationMap(): DelegationMap {
  const mapPath = join(process.cwd(), '.claude/agents/delegation-map.json');
  return loadJsonFile<DelegationMap>(mapPath, 'delegation map');
}

/**
 * Load agent configuration from .claude/agents/configs/{agentName}.json
 */
function loadAgentConfig(agentName: string): AgentConfig | null {
  const configPath = join(AGENTS_DIR, `${agentName}.json`);
  try {
    if (!existsSync(configPath)) {
      return null;
    }
    const content = readFileSync(configPath, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.warn(`Warning: Could not load config for ${agentName}: ${error}`);
    return null;
  }
}

/**
 * Check if a file path matches any delegation rule patterns
 */
function getAgentForFile(filePath: string, map: DelegationMap): string | null {
  for (const rule of map.delegation_rules) {
    // Check exclusions first
    if (rule.exclude) {
      const isExcluded = rule.exclude.some(pattern => minimatch(filePath, pattern));
      if (isExcluded) continue;
    }

    // Check if pattern matches
    if (minimatch(filePath, rule.pattern)) {
      return rule.primary_agent;
    }
  }
  return null;
}

/**
 * Check if user prompt contains MCP-triggering keywords
 */
function getAgentForKeywords(prompt: string, map: DelegationMap): string | null {
  const lowerPrompt = prompt.toLowerCase();

  // Check MCP routing rules
  for (const route of map.mcp_routing_rules.routing_map) {
    // Check if any keyword matches
    const hasKeyword = route.keywords.some(keyword =>
      lowerPrompt.includes(keyword.toLowerCase())
    );

    if (hasKeyword) {
      return route.primary_agent;
    }
  }

  // Check delegation rules for action keywords
  const actionKeywords = [
    'create', 'add', 'implement', 'fix', 'refactor',
    'update', 'modify', 'delete', 'remove', 'build',
    'write', 'generate', 'make', 'develop'
  ];

  // Special standalone keywords that don't need action words
  const standaloneKeywords = [
    { keywords: ['debug', 'investigate', 'troubleshoot'], agent: 'debugger' },
    { keywords: ['slow query', 'query performance', 'database performance'], agent: 'database-optimizer' },
  ];

  // Check standalone keywords first (don't require action words)
  for (const { keywords, agent } of standaloneKeywords) {
    if (keywords.some(kw => lowerPrompt.includes(kw))) {
      return agent;
    }
  }

  // Check for "optimize" + "query" combination
  if (lowerPrompt.includes('optimize') && lowerPrompt.includes('query')) {
    return 'database-optimizer';
  }

  // Check for breaking changes (requires careful orchestration)
  if (lowerPrompt.includes('breaking change')) {
    return 'backend-architect';
  }

  // Check for rename operations (TypeScript refactoring)
  if (lowerPrompt.includes('rename') && (lowerPrompt.includes('function') || lowerPrompt.includes('variable') || lowerPrompt.includes('class'))) {
    return 'typescript-pro';
  }

  const fileTypeKeywords = [
    // Test-related keywords first (higher priority than component keywords)
    { keywords: ['test', 'spec', 'e2e', 'unit test', 'integration test'], agent: 'test-automator' },
    { keywords: ['migration', 'schema', 'database', 'sql', 'rls', 'rpc'], agent: 'backend-architect' },
    { keywords: ['api', 'handler', 'endpoint', 'route', 'express'], agent: 'backend-architect' },
    { keywords: ['component', 'react', 'tsx', 'ui', 'button', 'form'], agent: 'frontend-developer' },
    { keywords: ['store', 'zustand', 'state'], agent: 'frontend-developer' },
  ];

  // Check for action + file type combinations
  const hasAction = actionKeywords.some(kw => lowerPrompt.includes(kw));

  if (hasAction) {
    for (const { keywords, agent } of fileTypeKeywords) {
      if (keywords.some(kw => lowerPrompt.includes(kw))) {
        return agent;
      }
    }
  }

  return null;
}

interface DelegationPlan {
  primary_agent: string;
  secondary_agents: string[];
  execution_mode: 'sequential' | 'parallel';
  rationale: string;
}

/**
 * Determine if secondary agents can run in parallel with primary
 */
function canRunInParallel(
  primary: string,
  secondaries: string[],
  prompt: string
): boolean {
  const lowerPrompt = prompt.toLowerCase();

  // Scenarios that MUST be sequential (dependencies exist)
  const sequentialPatterns = [
    'migration', 'schema change', 'breaking change',
    'refactor', 'rename', 'move file'
  ];

  if (sequentialPatterns.some(p => lowerPrompt.includes(p))) {
    return false;
  }

  // Independent validation agents can run in parallel
  const parallelAgents = ['code-reviewer-pro', 'test-automator', 'typescript-pro'];
  const allParallelizable = secondaries.every(agent => parallelAgents.includes(agent));

  // Primary creates code, secondaries validate → parallel
  if (['frontend-developer', 'backend-architect'].includes(primary) && allParallelizable) {
    return true;
  }

  return false;
}

/**
 * Get delegation plan with multiple agents
 */
export function getDelegationPlan(
  userPrompt: string,
  modifiedFile?: string
): DelegationPlan | null {
  const map = loadDelegationMap();
  let primaryAgent: string | null = null;
  let secondaryAgents: string[] = [];

  // 1. Check file pattern match first (most specific)
  if (modifiedFile) {
    const fileAgent = getAgentForFile(modifiedFile, map);
    if (fileAgent) {
      primaryAgent = fileAgent;

      // Find matching rule to get secondary agents
      const rule = map.delegation_rules.find(r =>
        minimatch(modifiedFile, r.pattern) &&
        (!r.exclude || !r.exclude.some(ex => minimatch(modifiedFile, ex)))
      );

      if (rule?.secondary_agents) {
        secondaryAgents = rule.secondary_agents;
      }
    }
  }

  // 2. Check keyword triggers (MCP operations, action words)
  if (!primaryAgent) {
    primaryAgent = getAgentForKeywords(userPrompt, map);

    if (primaryAgent) {
      // Try to find secondary agents from MCP routing rules first
      const mcpRoute = map.mcp_routing_rules.routing_map.find(r =>
        r.primary_agent === primaryAgent
      );

      if (mcpRoute?.secondary_agents) {
        secondaryAgents = mcpRoute.secondary_agents;
      } else {
        // Fallback: Find secondary agents from delegation_rules
        const delegationRule = map.delegation_rules.find(r =>
          r.primary_agent === primaryAgent
        );

        if (delegationRule?.secondary_agents) {
          secondaryAgents = delegationRule.secondary_agents;
        }
      }
    }
  }

  // 3. No delegation needed
  if (!primaryAgent) {
    return null;
  }

  // 4. Determine execution mode
  const executionMode = canRunInParallel(primaryAgent, secondaryAgents, userPrompt)
    ? 'parallel'
    : 'sequential';

  return {
    primary_agent: primaryAgent,
    secondary_agents: secondaryAgents,
    execution_mode: executionMode,
    rationale: executionMode === 'parallel'
      ? 'Independent validation agents can run concurrently'
      : 'Sequential execution required due to task dependencies'
  };
}

/**
 * Main router function (backward compatible)
 */
export function getAgentForRequest(
  userPrompt: string,
  modifiedFile?: string
): string | null {
  const plan = getDelegationPlan(userPrompt, modifiedFile);
  return plan?.primary_agent || null;
}

/**
 * Check if a session exists and is current
 */
async function ensureSession(sessionId?: string): Promise<string> {
  if (sessionId) {
    return sessionId;
  }

  // Check for existing session
  try {
    if (existsSync(CURRENT_SESSION_FILE)) {
      const existingSession = readFileSync(CURRENT_SESSION_FILE, 'utf-8').trim();
      if (existingSession) {
        return existingSession;
      }
    }
  } catch (error) {
    console.warn('Warning: Could not read current session file');
  }

  // Initialize new session
  console.log('Initializing new artifact session...');
  const newSession = await initSession();
  console.log(`Created session: ${newSession}\n`);
  return newSession;
}

/**
 * Build artifact instructions for an agent
 */
function buildArtifactInstructions(agentName: string, sessionId: string): string | null {
  const config = loadAgentConfig(agentName);

  if (!config?.artifacts?.enabled) {
    return null;
  }

  const threshold = config.artifacts.detail_threshold || 200;
  const customInstructions = config.artifacts.instructions || '';

  return `
## Artifact System Instructions

You have access to a persistent scratchpad for detailed implementation notes.

**Your scratchpad location**: \`.claude/artifacts/sessions/${sessionId}/${agentName}.md\`

**After completing each task**:
1. Write detailed implementation notes to your scratchpad using:
   \`\`\`typescript
   import { appendToScratchpad } from '../scripts/artifact-write.ts';
   await appendToScratchpad('${agentName}', {
     title: 'Task title',
     status: 'complete', // or 'in_progress', 'failed'
     summary: '2-3 sentences for orchestrator',
     filesModified: [
       { path: 'path/to/file', action: 'created', lineCount: 120 }
     ],
     decisions: ['Key decision 1', 'Key decision 2'],
     details: 'Full implementation notes here (will auto-collapse if > ${threshold} lines)'
   });
   \`\`\`

2. Return ONLY the summary to orchestrator (2-3 sentences)

**Format**:
✓ {summary}

**Example return**:
"✓ Added Button component with variant support. Created src/components/Button.tsx (120 lines), updated exports. Used forwardRef pattern for refs."

${customInstructions ? `\n**Additional Instructions**:\n${customInstructions}` : ''}
`;
}

interface ExecutionOptions {
  sessionId?: string;
  withArtifacts: boolean;
}

interface ExecutionResult {
  sessionId: string;
  agent: string;
  summary: string;
  artifactWritten: boolean;
  contextSummaries?: string;
}

/**
 * Execute delegation with artifact tracking
 */
export async function executeDelegation(
  userPrompt: string,
  modifiedFile?: string,
  options: ExecutionOptions = { withArtifacts: true }
): Promise<ExecutionResult | null> {
  const plan = getDelegationPlan(userPrompt, modifiedFile);

  if (!plan) {
    return null;
  }

  const sessionId = options.withArtifacts
    ? await ensureSession(options.sessionId)
    : 'no-session';

  // Register agent if using artifacts
  if (options.withArtifacts) {
    try {
      await registerAgent(plan.primary_agent, sessionId);
      console.log(`Registered agent: ${plan.primary_agent}`);
    } catch (error) {
      console.warn(`Warning: Failed to register agent: ${error}`);
    }
  }

  // Build enhanced prompt with artifact instructions
  let enhancedPrompt = userPrompt;
  if (options.withArtifacts) {
    const artifactInstructions = buildArtifactInstructions(plan.primary_agent, sessionId);
    if (artifactInstructions) {
      enhancedPrompt = `${userPrompt}\n\n${artifactInstructions}`;
    }
  }

  // In a real implementation, this would delegate to the agent
  // For now, we'll simulate the response
  console.log(`\n=== Delegating to ${plan.primary_agent} ===`);
  console.log(`Prompt: ${userPrompt}`);
  console.log(`Enhanced with artifacts: ${options.withArtifacts ? 'Yes' : 'No'}\n`);

  // Simulate agent response
  const summary = `Task delegated to ${plan.primary_agent}`;

  // Get updated context if using artifacts
  let contextSummaries = '';
  if (options.withArtifacts) {
    try {
      const allSummaries = await getAllAgentSummaries(sessionId);
      contextSummaries = allSummaries
        .map(s => `${s.agentName}: ${s.tasksCompleted} completed, ${s.tasksInProgress} in progress`)
        .join('\n');
    } catch (error) {
      console.warn(`Warning: Failed to get agent summaries: ${error}`);
    }
  }

  return {
    sessionId,
    agent: plan.primary_agent,
    summary,
    artifactWritten: options.withArtifacts,
    contextSummaries
  };
}

/**
 * CLI entry point (ESM-compatible)
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: delegation-router.ts "<user prompt>" [modified-file] [options]');
    console.error('');
    console.error('Examples:');
    console.error('  delegation-router.ts "Create migration for users"');
    console.error('  delegation-router.ts "Add button" src/components/Button.tsx');
    console.error('  delegation-router.ts "Add button" --plan  # Show full delegation plan');
    console.error('  delegation-router.ts "Add button" --execute  # Execute with artifacts');
    console.error('  delegation-router.ts "Add button" --execute --no-artifacts  # Execute without artifacts');
    console.error('  delegation-router.ts "Add button" --execute --session 2025-01-15_1430  # Use specific session');
    process.exit(1);
  }

  const showPlan = args.includes('--plan');
  const execute = args.includes('--execute');
  const withArtifacts = !args.includes('--no-artifacts');
  const sessionIndex = args.indexOf('--session');
  const sessionId = sessionIndex !== -1 && args[sessionIndex + 1] ? args[sessionIndex + 1] : undefined;

  // Filter out flags to get prompt and file
  const nonFlagArgs = args.filter(arg =>
    !arg.startsWith('--') &&
    (args.indexOf(arg) === 0 || args[args.indexOf(arg) - 1] !== '--session')
  );

  const prompt = nonFlagArgs[0];
  const file = nonFlagArgs[1];

  if (execute) {
    // Execute with artifact tracking
    executeDelegation(prompt, file, { sessionId, withArtifacts })
      .then(result => {
        if (result) {
          console.log('\n=== Execution Complete ===');
          console.log(`Session: ${result.sessionId}`);
          console.log(`Agent: ${result.agent}`);
          console.log(`Summary: ${result.summary}`);
          console.log(`Artifact written: ${result.artifactWritten}`);
          if (result.contextSummaries) {
            console.log(`\nAgent Status:\n${result.contextSummaries}`);
          }
        } else {
          console.log('none');
        }
      })
      .catch(error => {
        console.error(`Execution failed: ${error}`);
        process.exit(1);
      });
  } else if (showPlan) {
    const plan = getDelegationPlan(prompt, file);
    if (plan) {
      console.log(JSON.stringify(plan, null, 2));
    } else {
      console.log('none');
    }
  } else {
    const agent = getAgentForRequest(prompt, file);
    console.log(agent || 'none');
  }
}
