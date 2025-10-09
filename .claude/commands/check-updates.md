---
description: Check for updates to claude-config-template
---

Check if your claude-config-template installation is up to date.

This command:
- Compares your installed version with the latest GitHub commit
- Shows what's new if an update is available
- Provides the update command

Run the update check script:

```bash
bash .claude/scripts/check-updates.sh --force
```

If an update is available, you'll see upgrade instructions.

## Manual Update

To update your installation:

```bash
npx degit darrentmorgan/claude-config-template .claude-temp --force
cd .claude-temp
bash setup.sh --update
cd ..
rm -rf .claude-temp
```

This preserves your:
- `settings.local.json` (permissions and config)
- Custom agents (markdown files)
- Hooks and commands
- All customizations

## Version Information

Your current installation details are stored in `.claude/.version.json`.

Check it with:
```bash
cat .claude/.version.json | jq
```
