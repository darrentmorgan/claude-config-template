# Claude Code Configuration Template

A reusable, production-ready configuration system for Claude Code that brings autonomous development workflows to any project.

## 🚀 Features

- ✅ **Specialized Agent System** - Pattern-based delegation to 15+ expert agents
- ✅ **Automated Quality Gates** - Pre-commit hooks with linting, type-checking, and AI review
- ✅ **MCP Context Optimization** - 74% context reduction (~92k tokens saved)
- ✅ **Framework Agnostic** - Auto-detects and configures for React/Vue/Express/Next.js
- ✅ **Global Agent Sharing** - Consistent behavior across all projects
- ✅ **Custom Slash Commands** - `/generate-api`, `/create-component`, `/deploy`, etc.

## 📦 What's Included

```
claude-config-template/
├── agents/                    # Agent configurations
│   ├── configs/              # Agent-specific MCP settings
│   ├── delegation-map.json   # Pattern-based routing rules
│   └── mcp-mapping.json      # MCP server → agent mappings
├── hooks/                     # Quality gate hooks
│   ├── pre-commit.sh         # Linting + type-check + tests + AI review
│   ├── post-commit.sh        # CI/CD triggers
│   ├── tool-use.sh           # Auto-review after Edit/Write
│   └── test-result.sh        # Test analysis and debugging
├── commands/                  # Custom slash commands
│   ├── create-component.md   # Scaffold React components
│   ├── generate-api.md       # Generate Express endpoints
│   ├── deploy.md             # Autonomous deployment
│   └── run-qa.md             # E2E testing workflow
├── docs/                      # Documentation
│   └── MCP_DELEGATION_GUIDE.md
├── setup.sh                   # Interactive installation script
└── README.md                  # This file
```

## 🎯 Quick Start

### Installation

**Option 1: From this directory**
```bash
cd /path/to/your/project
/path/to/claude-config-template/setup.sh
```

**Option 2: Using degit (if published)**
```bash
cd /path/to/your/project
npx degit your-username/claude-config-template .claude-temp
.claude-temp/setup.sh
rm -rf .claude-temp
```

**Option 3: Using global command**
```bash
cd /path/to/your/project
/init-claude-config
```

### What the Setup Does

1. **Auto-detects your project**:
   - Package manager (npm/pnpm/yarn/bun)
   - Framework (React/Next.js/Vue/Express)
   - Project name

2. **Installs configuration**:
   - Copies files to `.claude/` directory
   - Replaces placeholders (`{{PKG_MANAGER}}`, `{{PROJECT_NAME}}`)
   - Makes hooks executable

3. **Optional global sharing**:
   - Links agent configs to `~/.claude/agents/shared/`
   - Ensures consistency across projects

4. **Git integration**:
   - Add to `.gitignore` (private config)
   - Or commit to repo (team-shared config)

## 🔧 Configuration

### Agent Delegation

Edit `.claude/agents/delegation-map.json` to customize:

```json
{
  "delegation_rules": [
    {
      "name": "React Components",
      "pattern": "**/*.tsx",
      "primary_agent": "frontend-developer",
      "context": {
        "framework": "React 18",
        "styling": "Tailwind CSS"
      }
    }
  ]
}
```

### Hooks

Customize `.claude/hooks/*.sh`:

```bash
# Disable AI judge in pre-commit.sh
# Comment out lines 59-68

# Adjust test command
if $PKG_MANAGER test:unit --run; then  # Changed from 'test'
```

### Commands

Adapt `.claude/commands/*.md` to your stack:

- Update API generation for different frameworks
- Customize component scaffolding
- Add project-specific workflows

### Permissions

Configure `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(git add:*)",
      "Bash(pnpm:*)",      // Change to your package manager
      "Task(*:*)"
    ]
  }
}
```

## 🎨 Usage

### Slash Commands

After installation, use these commands:

```bash
/generate-api createProject POST    # Generate Express endpoint
/create-component Button            # Scaffold React component
/deploy                             # Autonomous deployment workflow
/run-qa                             # E2E testing with AI review
```

### Quality Gates

Hooks run automatically:

- **Pre-commit**: Linting → Type-check → Tests → AI review
- **Post-commit**: CI/CD trigger notifications
- **Tool-use**: Auto-format and quick checks after Edit/Write
- **Test-result**: Analyze failures, suggest fixes

### Agent Delegation

File changes auto-route to appropriate agents:

- `*.tsx` → `frontend-developer`
- `src/server/**` → `backend-architect`
- `*.test.ts` → `test-automator`
- API contracts → `typescript-pro`
- Migrations → `backend-architect`

## 🌍 Global Agent Sharing

### Setup Global Agents

The setup script offers global agent sharing:

```bash
Enable global agent sharing? (y/n): y
```

This creates:
```
~/.claude/agents/shared/
├── configs/              # Shared across all projects
└── mcp-mapping.json
```

Projects link to shared configs:
```bash
.claude/agents/configs → ~/.claude/agents/shared/configs
```

### Benefits

1. **Single source of truth**: Update once, applies everywhere
2. **Consistency**: Same agent behavior across projects
3. **Easy updates**: Pull template, copy to `~/.claude/agents/shared/`

### Update Shared Agents

```bash
cd /path/to/claude-config-template
git pull
cp -r agents/configs/* ~/.claude/agents/shared/configs/
```

## 📊 Context Optimization

This template implements MCP delegation for massive context savings:

| Configuration | Main Agent Context | Savings |
|--------------|-------------------|---------|
| **Before** (all MCP in main) | 125k tokens | - |
| **After** (delegated MCP) | 33k tokens | **74% reduction** |

### How It Works

- Main orchestrator has **zero MCP servers**
- Tasks requiring MCP auto-route to specialized agents
- Agents load MCP only when invoked
- Return summaries, not full responses

See `.claude/docs/MCP_DELEGATION_GUIDE.md` for details.

## 🔄 Updating Template

### For a Single Project

```bash
cd /path/to/claude-config-template
git pull
./setup.sh  # Will prompt before overwriting
```

### For All Projects (via global agents)

```bash
cd /path/to/claude-config-template
git pull
cp -r agents/configs/* ~/.claude/agents/shared/configs/
```

All linked projects get updates immediately.

## 📚 Documentation

- **Agent System**: `.claude/docs/MCP_DELEGATION_GUIDE.md`
- **Hooks**: `.claude/hooks/README.md`
- **Commands**: `.claude/commands/*.md`
- **Global Init**: `~/.claude/commands/init-claude-config.md`

## 🤝 Distribution

### As GitHub Template

1. Create new repo from this template
2. Users install via:
   ```bash
   npx degit your-username/claude-config-template .claude-temp
   .claude-temp/setup.sh
   ```

### As NPM Package

1. Publish to npm (future)
2. Users install via:
   ```bash
   npx @your-org/init-claude-config
   ```

### As Git Submodule

1. Add to project:
   ```bash
   git submodule add https://github.com/your-username/claude-config-template .claude-template
   .claude-template/setup.sh
   ```

2. Update:
   ```bash
   git submodule update --remote
   .claude-template/setup.sh
   ```

## 🐛 Troubleshooting

**Setup fails with permission error**
```bash
chmod +x setup.sh
./setup.sh
```

**Hooks not triggering**
```bash
chmod +x .claude/hooks/*.sh
cat .claude/settings.local.json  # Verify hook config
```

**Global agents not found**
```bash
ls ~/.claude/agents/shared  # Should exist
# If missing, re-run setup and choose "y" for global sharing
```

**Want to uninstall**
```bash
rm -rf .claude
sed -i '/.claude\//d' .gitignore
```

## 📝 Customization Examples

### Change Package Manager

```bash
# Find and replace in hooks
sed -i 's/pnpm/npm/g' .claude/hooks/*.sh
```

### Adapt for Different Framework

Edit `.claude/agents/delegation-map.json`:

```json
{
  "name": "Vue Components",
  "pattern": "**/*.vue",
  "context": {
    "framework": "Vue 3",
    "styling": "Tailwind CSS"
  }
}
```

### Add Custom Agent

1. Create config: `.claude/agents/configs/my-agent.json`
2. Update delegation rules in `delegation-map.json`
3. Add to MCP routing in `mcp-mapping.json`

## 🚀 Next Steps

After installation:

1. ✅ Review `.claude/settings.local.json` for permissions
2. ✅ Customize `.claude/agents/delegation-map.json` for your project
3. ✅ Try `/generate-api` or `/create-component`
4. ✅ Make a commit (quality gate will run)
5. ✅ Read `.claude/docs/MCP_DELEGATION_GUIDE.md`

## 📄 License

MIT

---

**Created by**: [Your Name]
**Template Version**: 1.0.0
**Last Updated**: 2025-10-08
