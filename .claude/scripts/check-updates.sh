#!/bin/bash
# Check for updates to claude-config-template
# Usage: bash .claude/scripts/check-updates.sh [--force]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
VERSION_FILE="$PROJECT_ROOT/.claude/.version.json"
CACHE_FILE="$PROJECT_ROOT/.claude/.update-check-cache"
REPO="darrentmorgan/claude-config-template"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if force flag is set
FORCE=false
if [[ "$1" == "--force" ]]; then
    FORCE=true
fi

# Check cache (skip if less than 24 hours old, unless --force)
if [ -f "$CACHE_FILE" ] && [ "$FORCE" = false ]; then
    CACHE_AGE=$(($(date +%s) - $(stat -f %m "$CACHE_FILE" 2>/dev/null || stat -c %Y "$CACHE_FILE" 2>/dev/null)))
    if [ $CACHE_AGE -lt 86400 ]; then  # 24 hours
        if [ -f "$VERSION_FILE" ]; then
            LAST_CHECK=$(jq -r '.lastChecked // "unknown"' "$VERSION_FILE")
            echo -e "${BLUE}ℹ Already checked recently (${LAST_CHECK})${NC}"
            echo "Use --force to check again"
        fi
        exit 0
    fi
fi

# Read local version
if [ ! -f "$VERSION_FILE" ]; then
    echo -e "${YELLOW}⚠ No version file found. Please reinstall the template.${NC}"
    exit 1
fi

LOCAL_VERSION=$(jq -r '.installedVersion // "unknown"' "$VERSION_FILE")
LOCAL_COMMIT=$(jq -r '.gitCommitHash // "unknown"' "$VERSION_FILE")
INSTALL_DATE=$(jq -r '.installedDate // "unknown"' "$VERSION_FILE")

echo -e "${BLUE}Checking for updates...${NC}"
echo "Current version: $LOCAL_VERSION ($LOCAL_COMMIT)"
echo "Installed: $INSTALL_DATE"
echo ""

# Fetch latest commit from GitHub API
GITHUB_API="https://api.github.com/repos/$REPO/commits/main"
LATEST_DATA=$(curl -s "$GITHUB_API")

# Check if API call was successful
if echo "$LATEST_DATA" | jq -e '.sha' > /dev/null 2>&1; then
    LATEST_COMMIT=$(echo "$LATEST_DATA" | jq -r '.sha' | cut -c1-7)
    LATEST_DATE=$(echo "$LATEST_DATA" | jq -r '.commit.author.date')
    LATEST_MESSAGE=$(echo "$LATEST_DATA" | jq -r '.commit.message' | head -n1)

    # Update cache
    touch "$CACHE_FILE"

    # Update version file with last checked time
    jq ".lastChecked = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"" "$VERSION_FILE" > "$VERSION_FILE.tmp"
    mv "$VERSION_FILE.tmp" "$VERSION_FILE"

    # Compare versions
    if [ "$LOCAL_COMMIT" = "$LATEST_COMMIT" ]; then
        echo -e "${GREEN}✓ You're up to date!${NC}"
        echo "Latest: $LATEST_COMMIT"
    else
        echo -e "${YELLOW}╭─────────────────────────────────────────────────╮${NC}"
        echo -e "${YELLOW}│ 🚀 Update Available!                            │${NC}"
        echo -e "${YELLOW}│                                                 │${NC}"
        echo -e "${YELLOW}│ Installed: $LOCAL_COMMIT                               │${NC}"
        echo -e "${YELLOW}│ Latest:    $LATEST_COMMIT                               │${NC}"
        echo -e "${YELLOW}│                                                 │${NC}"
        echo -e "${YELLOW}│ Latest change:                                  │${NC}"
        echo -e "${YELLOW}│ $LATEST_MESSAGE${NC}"
        echo -e "${YELLOW}│                                                 │${NC}"
        echo -e "${YELLOW}│ Update now:                                     │${NC}"
        echo -e "${YELLOW}│ npx degit $REPO .claude-temp --force &&         │${NC}"
        echo -e "${YELLOW}│   cd .claude-temp && bash setup.sh --update &&  │${NC}"
        echo -e "${YELLOW}│   cd .. && rm -rf .claude-temp                  │${NC}"
        echo -e "${YELLOW}╰─────────────────────────────────────────────────╯${NC}"
        exit 2  # Exit code 2 = update available
    fi
else
    echo -e "${YELLOW}⚠ Could not check for updates (GitHub API error)${NC}"
    echo "Try again later or check manually: https://github.com/$REPO"
    exit 3  # Exit code 3 = API error
fi
