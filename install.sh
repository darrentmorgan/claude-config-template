#!/bin/bash
# Claude Config Template - One-Command Installer with Progress
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/darrentmorgan/claude-config-template/main/install.sh)

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Spinner animation
spin() {
    local pid=$1
    local message=$2
    local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'

    while kill -0 $pid 2>/dev/null; do
        local temp=${spinstr#?}
        printf "\r${BLUE}[%c]${NC} %s" "$spinstr" "$message"
        spinstr=$temp${spinstr%"$temp"}
        sleep 0.1
    done
    printf "\r${GREEN}[✓]${NC} %s\n" "$message"
}

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Claude Config Template Installer     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Download template
echo -e "${YELLOW}Step 1/4:${NC} Downloading template..."
npx degit darrentmorgan/claude-config-template .claude-temp --force > /dev/null 2>&1 &
spin $! "Downloading latest template from GitHub"

# Step 2: Navigate to temp directory
echo -e "${YELLOW}Step 2/4:${NC} Preparing installation..."
cd .claude-temp
echo -e "${GREEN}[✓]${NC} Ready to install"

# Step 3: Run setup script
echo -e "${YELLOW}Step 3/4:${NC} Running interactive setup..."
echo ""
bash setup.sh

# Step 4: Cleanup
echo ""
echo -e "${YELLOW}Step 4/4:${NC} Cleaning up temporary files..."
cd ..
rm -rf .claude-temp
echo -e "${GREEN}[✓]${NC} Cleanup complete"

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}Installation complete! 🎉${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
