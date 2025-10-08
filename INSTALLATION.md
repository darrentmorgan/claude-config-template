# Installation Guide

## ✨ One-Command Install (Recommended)

### Fresh Install

**Method 1: Wrapper Script (Best Visual Feedback)**

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/darrentmorgan/claude-config-template/main/install.sh)
```

This provides the best installation experience with:
- 🔄 Animated spinner during GitHub download
- 📊 Progress bars for file operations
- ✅ Clear step-by-step status updates
- 🧹 Automatic cleanup

**Method 2: Direct Install (Alternative)**

```bash
npx degit darrentmorgan/claude-config-template .claude-temp && cd .claude-temp && bash setup.sh && cd .. && rm -rf .claude-temp
```

Both methods will:
- ✅ Download latest template
- ✅ Run interactive setup with real-time progress indicators
- ✅ Copy all files to `.claude/` directory (with progress bars)
- ✅ Install all agent configs with MCP server assignments
- ✅ Set up hooks and scripts
- ✅ Clean up temporary files

**Visual Feedback**: The installer shows:
- 🔄 Download progress spinner
- 📊 Progress bars for file copying operations
- ⏳ Real-time status updates
- 📁 Which files/directories are being processed

### Update Existing Installation

```bash
npx degit darrentmorgan/claude-config-template .claude-temp --force && cd .claude-temp && bash setup.sh && cd .. && rm -rf .claude-temp
```

When prompted "`.claude` directory already exists", choose:
- **y** to overwrite (recommended for updates)
- **n** to cancel

---

## 📋 What Gets Installed

```
your-project/
├── .claude/                          # Main config directory
│   ├── agents/
│   │   ├── configs/                  # ✅ Agent MCP assignments
│   │   │   ├── backend-architect.json     (supabase)
│   │   │   ├── database-optimizer.json    (supabase)
│   │   │   ├── qa-expert.json             (chrome-devtools, playwright)
│   │   │   ├── test-automator.json        (chrome-devtools, playwright)
│   │   │   ├── documentation-expert.json  (Context7)
│   │   │   └── ...
│   │   ├── delegation-map.json       # ✅ Routing rules
│   │   └── mcp-mapping.json          # ✅ MCP server definitions
│   ├── hooks/
│   │   ├── pre-request-router.sh     # ✅ Parallel execution hook
│   │   ├── pre-commit.sh             # Code review
│   │   ├── post-commit.sh            # CI/CD
│   │   └── tool-use.sh               # Auto-review
│   ├── scripts/
│   │   ├── delegation-router.ts      # ✅ Parallel detection
│   │   └── update-claude-md.sh       # CLAUDE.md updater
│   ├── commands/                     # Slash commands
│   ├── docs/                         # Documentation
│   │   ├── PARALLEL_EXECUTION_GUIDE.md
│   │   └── ...
│   ├── logs/                         # Log files
│   └── settings.local.json           # Permissions
```

---

## 🔧 Manual Installation (Advanced)

If you prefer manual control:

```bash
# 1. Download template
npx degit darrentmorgan/claude-config-template claude-template

# 2. Review setup.sh
cat claude-template/setup.sh

# 3. Run setup interactively
cd claude-template
bash setup.sh

# 4. Cleanup
cd ..
rm -rf claude-template
```

---

## 🔄 Update Without Overwriting Customizations

If you've customized your config and want to update specific files only:

```bash
# Download template
npx degit darrentmorgan/claude-config-template .claude-temp --force

# Update specific files
cp .claude-temp/.claude/scripts/delegation-router.ts .claude/scripts/
cp .claude-temp/.claude/hooks/pre-request-router.sh .claude/hooks/

# Update agent configs (⚠️ overwrites customizations)
cp -r .claude-temp/.claude/agents/configs/ .claude/agents/

# Update documentation
cp -r .claude-temp/.claude/docs/ .claude/

# Cleanup
rm -rf .claude-temp

# Make executable
chmod +x .claude/hooks/*.sh .claude/scripts/*.ts
```

---

## ✅ Verify Installation

```bash
# Test delegation router
npx tsx .claude/scripts/delegation-router.ts "Add Button component" --plan

# Expected output:
# {
#   "primary_agent": "frontend-developer",
#   "secondary_agents": ["code-reviewer-pro", "test-automator"],
#   "execution_mode": "parallel",
#   "rationale": "Independent validation agents can run concurrently"
# }

# Check agent configs exist
ls -la .claude/agents/configs/

# Should show:
# backend-architect.json
# database-optimizer.json
# qa-expert.json
# test-automator.json
# etc.

# Check MCP assignments
cat .claude/agents/configs/backend-architect.json | jq '.mcp_servers'
# Output: ["supabase"]

cat .claude/agents/configs/qa-expert.json | jq '.mcp_servers'
# Output: ["chrome-devtools", "playwright"]
```

---

## 🏗️ Template Structure Explained

### Why Files Exist in Multiple Places

The template repository has files in both locations:

```
claude-config-template/           # Template repo
├── agents/                       # For reference/testing
├── hooks/                        # For reference/testing
├── scripts/                      # For reference/testing
├── docs/                         # For reference/testing
├── .claude/                      # ⚠️ GITIGNORED - not tracked
│   └── (gets created during setup)
└── setup.sh                      # Copies to .claude/
```

**During installation**:
- `setup.sh` copies `agents/`, `hooks/`, `scripts/`, `docs/` → `.claude/`
- Your project gets clean `.claude/` directory
- No duplicate files in your project root

**Why root files exist in template**:
1. Testing the template itself
2. Reference for development
3. Template evolution

**Your project structure after install**:
```
your-project/
├── src/                          # Your code
├── .claude/                      # ✅ All config here
│   ├── agents/configs/           # ✅ MCP assignments
│   ├── hooks/                    # ✅ Automation
│   └── scripts/                  # ✅ Utilities
└── (no duplicate files)
```

---

## 🎯 Quick Start After Install

```bash
# 1. Test parallel execution
npx tsx .claude/scripts/delegation-router.ts "Add login form" --plan

# 2. Review agent configs
cat .claude/agents/configs/backend-architect.json

# 3. Check delegation map
cat .claude/agents/delegation-map.json | jq '.execution_strategy'

# 4. Read documentation
ls .claude/docs/
```

---

## 🐛 Troubleshooting

### "delegation-router.ts not found"

```bash
# Check if .claude/scripts exists
ls -la .claude/scripts/

# If missing, re-run setup
npx degit darrentmorgan/claude-config-template .claude-temp --force
cd .claude-temp && bash setup.sh && cd .. && rm -rf .claude-temp
```

### "Agent configs missing MCP servers"

```bash
# Check if configs exist
ls .claude/agents/configs/

# If empty, re-copy configs
npx degit darrentmorgan/claude-config-template .claude-temp --force
cp -r .claude-temp/.claude/agents/configs/ .claude/agents/
rm -rf .claude-temp
```

### "Hook not executable"

```bash
# Make all hooks executable
chmod +x .claude/hooks/*.sh .claude/scripts/*.ts
```

---

## 📚 Next Steps

After installation:

1. **Read the guides**:
   - `.claude/docs/PARALLEL_EXECUTION_GUIDE.md`
   - `.claude/docs/AGENT_REFERENCE.md`
   - `.claude/docs/MCP_DELEGATION_GUIDE.md`

2. **Customize for your project**:
   - Edit `.claude/agents/delegation-map.json`
   - Adjust `.claude/settings.local.json`

3. **Test delegation**:
   ```bash
   # Try different scenarios
   npx tsx .claude/scripts/delegation-router.ts "Create API endpoint" --plan
   npx tsx .claude/scripts/delegation-router.ts "Debug failing test" --plan
   npx tsx .claude/scripts/delegation-router.ts "Optimize database query" --plan
   ```

4. **Update global CLAUDE.md** (optional):
   ```bash
   bash .claude/scripts/update-claude-md.sh
   ```

---

## 🔗 Related Documentation

- [Parallel Execution Guide](docs/PARALLEL_EXECUTION_GUIDE.md)
- [Quick Reference](docs/PARALLEL_EXECUTION_QUICK_REF.md)
- [Test Results](TEST_RESULTS.md)
- [Implementation Details](PARALLEL_EXECUTION_IMPLEMENTATION.md)

---

## ❓ FAQ

**Q: Do I need to install this in every project?**
A: Yes, each project gets its own `.claude/` directory. However, you can enable global agent sharing to reduce duplication.

**Q: Can I commit `.claude/` to git?**
A: Yes! During setup, you'll be asked if you want to add `.claude/` to `.gitignore` (private config) or commit it (shared team config).

**Q: How do I update to new versions?**
A: Re-run the one-command install and choose "y" when asked to overwrite.

**Q: What if I customized my config?**
A: Backup first, then use manual update to copy only specific files you want to update.

**Q: Do agent MCP servers work automatically?**
A: Yes! Each agent's `.json` config specifies which MCP servers it loads. The Task tool reads this automatically.

---

**🚀 Ready to install? Copy the one-command installer at the top of this guide!**
