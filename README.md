# Claude Code Configuration Template

[![GitHub](https://img.shields.io/badge/GitHub-darrentmorgan%2Fclaude--config--template-blue?logo=github)](https://github.com/darrentmorgan/claude-config-template)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready configuration system for Claude Code that brings autonomous development workflows, specialized AI agents, and quality automation to any project.

## 🚀 Quick Install

**Fresh Installation:**
```bash
npx degit darrentmorgan/claude-config-template .claude-temp && cd .claude-temp && bash setup.sh && cd .. && rm -rf .claude-temp
```

**Update Existing:**
```bash
npx degit darrentmorgan/claude-config-template .claude-temp --force && cd .claude-temp && bash setup.sh --update && cd .. && rm -rf .claude-temp
```

## What It Does

This template transforms Claude Code into an autonomous development system with:

- **18+ specialized AI agents** that automatically handle specific tasks (frontend, backend, testing, security, etc.)
- **Automated quality gates** that run linting, type-checking, and tests before every commit
- **Smart task routing** that delegates work to the right agent based on file patterns
- **Pre-built workflows** for common tasks like API generation, component creation, and deployment

Think of it as giving Claude Code a team of expert developers, each focused on their specialty, with automatic coordination between them.

## ✨ Key Features

- **Specialized Agent System** - 18+ expert agents (frontend, backend, testing, security, docs, etc.)
- **Automated Quality Gates** - Pre-commit hooks with linting, type-checking, tests, and AI review
- **Smart Delegation** - Pattern-based routing sends tasks to the right agent automatically
- **Scout → Plan → Build** - Multi-phase workflows with TDD enforcement
- **Custom Slash Commands** - `/create-component`, `/generate-api`, `/deploy`, `/run-qa`
- **Framework Agnostic** - Auto-detects React/Vue/Next.js/Express and configures accordingly

## 📦 What's Included

```
.claude/
├── agents/
│   ├── configs/              # 18+ specialized agent configurations
│   │   ├── frontend-developer.json
│   │   ├── backend-architect.json
│   │   ├── test-engineer.json
│   │   └── ... (15+ more)
│   ├── delegation-map.json   # Routing rules (*.tsx → frontend-developer)
│   └── mcp-mapping.json      # MCP server assignments per agent
│
├── hooks/                     # Quality automation
│   ├── tool.bash.block.sh    # Enforce fast tools (Grep, not grep)
│   ├── tool-use.sh           # Auto-review after Edit/Write
│   ├── pre-commit.sh         # Linting + type-check + tests
│   └── post-git-push.sh      # CI/CD notifications
│
├── commands/                  # Slash commands
│   ├── scout.md              # Phase 1: Context identification
│   ├── plan_w_docs.md        # Phase 2: TDD planning
│   ├── build.md              # Phase 3: Implementation
│   ├── create-component.md   # Component scaffolding
│   ├── generate-api.md       # API endpoint generation
│   └── deploy.md             # Deployment automation
│
├── docs/                      # Complete documentation
│   ├── AGENT_REFERENCE.md
│   ├── DELEGATION.md
│   └── ... (detailed guides)
│
└── settings.local.json        # Permissions and hook configuration
```

## 🎯 Installation

### What the Setup Script Does

1. **Auto-detects your project:**
   - Package manager (npm/pnpm/yarn/bun)
   - Framework (React/Next.js/Vue/Express)
   - Project name

2. **Installs complete configuration:**
   - Copies all files to `.claude/` directory
   - Configures agent specializations
   - Replaces placeholders with your project details
   - Makes hooks executable

3. **Optional features:**
   - Install fast CLI tools (ripgrep, fd, fzf - 10x faster search)
   - Link to global agent configs for consistency across projects
   - Add to `.gitignore` or commit for team sharing

### Verify Installation

```bash
# Test routing
npx tsx .claude/scripts/delegation-router.ts "Add Button component" --plan

# See installed agents
ls .claude/agents/configs/

# Check hook configuration
cat .claude/settings.local.json
```

## 🎨 Usage

### Slash Commands

**Single-phase (focused tasks):**
```bash
/create-component Button              # Scaffold React component
/generate-api createProject POST      # Generate API endpoint
/deploy                               # Autonomous deployment
/run-qa                              # E2E testing workflow
```

**Multi-phase (autonomous workflows):**
```bash
/scout_plan_build "Add dark mode toggle"   # Full Scout → Plan → Build
/scout "User profile management"          # Phase 1: Find relevant code
/plan_w_docs                              # Phase 2: Create TDD plan
/build /path/to/plan.md                   # Phase 3: Implement with tests
```

### Quality Gates (Automatic)

Hooks run automatically on file changes and commits:

- **tool.bash.block.sh** - Enforces fast tools (Grep not grep, Glob not find)
- **tool-use.sh** - Auto-review after Edit/Write operations
- **pre-commit.sh** - Runs linting → type-check → tests before commit
- **post-git-push.sh** - Notifies CI/CD of new changes

### Agent Delegation (Automatic)

File patterns automatically route to specialized agents:

- `*.tsx`, `*.jsx` → **frontend-developer**
- `src/server/**/*` → **backend-architect**
- `*.test.ts` → **test-engineer**
- `*.md` → **documentation-expert**
- Security issues → **security-auditor**

## ⚙️ Configuration

All configuration lives in `.claude/`:

- **Agent routing**: Edit `.claude/agents/delegation-map.json`
- **Hooks**: Customize `.claude/hooks/*.sh` scripts
- **Permissions**: Configure `.claude/settings.local.json`
- **Commands**: Adapt `.claude/commands/*.md` to your stack

**Example: Change package manager**
```bash
# Update hooks to use npm instead of pnpm
sed -i '' 's/pnpm/npm/g' .claude/hooks/*.sh
```

See `.claude/docs/` for detailed configuration guides.

## 📚 Documentation

Complete guides are in `.claude/docs/`:

- **AGENT_REFERENCE.md** - All 18+ agents and their specialties
- **DELEGATION.md** - How routing and task delegation works
- **WORKFLOWS.md** - Scout → Plan → Build guide
- **TROUBLESHOOTING.md** - Common issues and solutions
- **HOOK_ERRORS_FIX.md** - Hook path resolution guide

## 🔄 Updates

**Update this project:**
```bash
cd /path/to/claude-config-template
git pull
./setup.sh --update
```

**Update other projects using this template:**
```bash
# Re-run the quick install command in the project directory
npx degit darrentmorgan/claude-config-template .claude-temp --force && cd .claude-temp && bash setup.sh --update && cd .. && rm -rf .claude-temp
```

## 🐛 Common Issues

**Setup fails:**
```bash
chmod +x setup.sh && ./setup.sh
```

**Hooks not running:**
```bash
chmod +x .claude/hooks/*.sh
```

**Hook path errors:** See `.claude/docs/HOOK_ERRORS_FIX.md`

For detailed troubleshooting, see `.claude/docs/TROUBLESHOOTING.md`

## 🚀 Next Steps

After installation:

1. Review `.claude/settings.local.json` for permissions
2. Try `/create-component MyButton` to test agent delegation
3. Make a test commit to verify quality gates
4. Read `.claude/docs/AGENT_REFERENCE.md` to understand available agents
5. Customize `.claude/agents/delegation-map.json` for your project

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Credits

Built with [Claude Code](https://claude.com/code) by [Darren Morgan](https://github.com/darrentmorgan)

## 🔗 Links

- **Repository**: https://github.com/darrentmorgan/claude-config-template
- **Issues**: https://github.com/darrentmorgan/claude-config-template/issues
- **Discussions**: https://github.com/darrentmorgan/claude-config-template/discussions

---

⭐ **If you find this useful, please star the repo!**

**Version**: 1.0.0 | **Last Updated**: 2025-10-11
