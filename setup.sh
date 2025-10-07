#!/bin/bash
# Claude Config Template Setup Script
# Interactive setup for .claude configuration in any project

set -e

echo "🚀 Claude Code Configuration Setup"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detect current directory
CURRENT_DIR=$(pwd)
PROJECT_NAME=$(basename "$CURRENT_DIR")

echo -e "${BLUE}Current directory: $CURRENT_DIR${NC}"
echo -e "${BLUE}Detected project name: $PROJECT_NAME${NC}"
echo ""

# Step 1: Detect package manager
echo -e "${YELLOW}Step 1: Detecting package manager...${NC}"

PKG_MANAGER=""
if [ -f "package-lock.json" ]; then
    PKG_MANAGER="npm"
elif [ -f "pnpm-lock.yaml" ]; then
    PKG_MANAGER="pnpm"
elif [ -f "yarn.lock" ]; then
    PKG_MANAGER="yarn"
elif [ -f "bun.lockb" ]; then
    PKG_MANAGER="bun"
else
    echo -e "${YELLOW}No lock file found. Which package manager do you use?${NC}"
    echo "1) npm"
    echo "2) pnpm"
    echo "3) yarn"
    echo "4) bun"
    read -p "Select (1-4): " pm_choice
    case $pm_choice in
        1) PKG_MANAGER="npm" ;;
        2) PKG_MANAGER="pnpm" ;;
        3) PKG_MANAGER="yarn" ;;
        4) PKG_MANAGER="bun" ;;
        *) echo "Invalid choice. Defaulting to npm"; PKG_MANAGER="npm" ;;
    esac
fi

echo -e "${GREEN}✓ Package manager: $PKG_MANAGER${NC}"
echo ""

# Step 2: Detect framework (optional)
echo -e "${YELLOW}Step 2: Detecting framework...${NC}"

FRAMEWORK="generic"
if [ -f "package.json" ]; then
    if grep -q '"react"' package.json; then
        FRAMEWORK="react"
    elif grep -q '"next"' package.json; then
        FRAMEWORK="nextjs"
    elif grep -q '"vue"' package.json; then
        FRAMEWORK="vue"
    elif grep -q '"express"' package.json; then
        FRAMEWORK="express"
    fi
fi

echo -e "${GREEN}✓ Framework: $FRAMEWORK${NC}"
echo ""

# Step 3: Confirm or customize
echo -e "${YELLOW}Step 3: Configuration Summary${NC}"
echo "  Project Name: $PROJECT_NAME"
echo "  Package Manager: $PKG_MANAGER"
echo "  Framework: $FRAMEWORK"
echo ""
read -p "Continue with this configuration? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "Setup cancelled."
    exit 0
fi

# Step 4: Copy files to .claude directory
echo ""
echo -e "${YELLOW}Step 4: Installing .claude configuration...${NC}"

# Create .claude directory if it doesn't exist
if [ -d ".claude" ]; then
    echo -e "${YELLOW}⚠  .claude directory already exists.${NC}"
    read -p "Overwrite existing configuration? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
    rm -rf .claude
fi

mkdir -p .claude

# Copy directory structure
echo "📁 Copying configuration files..."
cp -r agents .claude/
cp -r hooks .claude/
cp -r commands .claude/
cp -r docs .claude/ 2>/dev/null || true
cp -r scripts .claude/ 2>/dev/null || true
cp settings.local.json .claude/

# Step 5: Replace placeholders
echo ""
echo -e "${YELLOW}Step 5: Customizing configuration...${NC}"

# Function to replace placeholders in files
replace_placeholders() {
    local file=$1
    if [ -f "$file" ]; then
        # Replace {{PKG_MANAGER}}
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|{{PKG_MANAGER}}|$PKG_MANAGER|g" "$file"
            sed -i '' "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" "$file"
            sed -i '' "s|{{FRAMEWORK}}|$FRAMEWORK|g" "$file"
        else
            sed -i "s|{{PKG_MANAGER}}|$PKG_MANAGER|g" "$file"
            sed -i "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" "$file"
            sed -i "s|{{FRAMEWORK}}|$FRAMEWORK|g" "$file"
        fi
    fi
}

# Replace in all hook files
for file in .claude/hooks/*.sh; do
    replace_placeholders "$file"
    chmod +x "$file"
done

# Replace in config files
replace_placeholders ".claude/settings.local.json"
replace_placeholders ".claude/agents/delegation-map.json"

echo -e "${GREEN}✓ Placeholders replaced${NC}"

# Step 6: Setup global agent sharing (optional)
echo ""
echo -e "${YELLOW}Step 6: Global Agent Sharing (Optional)${NC}"
echo "Would you like to use shared agents from ~/.claude/agents?"
echo "This reduces duplication across projects."
read -p "Enable global agent sharing? (y/n): " share_agents

if [ "$share_agents" = "y" ]; then
    GLOBAL_AGENTS_DIR="$HOME/.claude/agents/shared"

    if [ ! -d "$GLOBAL_AGENTS_DIR" ]; then
        echo "Creating global agents directory..."
        mkdir -p "$GLOBAL_AGENTS_DIR"

        # Copy agent configs to global location
        cp -r .claude/agents/configs "$GLOBAL_AGENTS_DIR/"
        cp .claude/agents/mcp-mapping.json "$GLOBAL_AGENTS_DIR/"

        echo -e "${GREEN}✓ Global agents created at ~/.claude/agents/shared${NC}"
    fi

    # Create symlink
    rm -rf .claude/agents/configs
    ln -s "$GLOBAL_AGENTS_DIR/configs" .claude/agents/configs

    echo -e "${GREEN}✓ Linked to global agents${NC}"
else
    echo "Using local agents only"
fi

# Step 7: Create necessary directories
echo ""
echo -e "${YELLOW}Step 7: Creating log directories...${NC}"
mkdir -p .claude/logs

echo -e "${GREEN}✓ Log directories created${NC}"

# Step 8: Git setup
echo ""
echo -e "${YELLOW}Step 8: Git Integration${NC}"

if [ -d ".git" ]; then
    echo "Git repository detected."
    echo "Would you like to:"
    echo "1) Add .claude to .gitignore (private config)"
    echo "2) Commit .claude to repository (shared config)"
    echo "3) Skip git setup"
    read -p "Select (1-3): " git_choice

    case $git_choice in
        1)
            if ! grep -q "^\.claude/$" .gitignore 2>/dev/null; then
                echo ".claude/" >> .gitignore
                echo -e "${GREEN}✓ Added .claude to .gitignore${NC}"
            fi
            ;;
        2)
            git add .claude
            echo -e "${YELLOW}Run 'git commit' to save .claude configuration${NC}"
            ;;
        3)
            echo "Skipped git setup"
            ;;
    esac
else
    echo "No git repository found - skipping git integration"
fi

# Step 9: Final instructions
echo ""
echo -e "${GREEN}=================================="
echo "✅ Setup Complete!"
echo "==================================${NC}"
echo ""
echo "Your .claude configuration is ready to use."
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Review .claude/settings.local.json for permissions"
echo "2. Customize .claude/agents/delegation-map.json for your project"
echo "3. Try a command: /generate-api or /create-component"
echo "4. Hooks will automatically run on Edit/Write/Commit"
echo ""
echo -e "${YELLOW}Documentation:${NC}"
echo "  - Agent system: .claude/docs/MCP_DELEGATION_GUIDE.md"
echo "  - Hooks: .claude/hooks/README.md"
echo "  - Commands: .claude/commands/*.md"
echo ""
echo -e "${GREEN}Happy coding with Claude! 🚀${NC}"
