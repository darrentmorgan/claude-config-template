#!/bin/bash
# Memory Guard Hook
# Checks Claude Code process memory usage and blocks requests if too high

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default limit: 7GB (80% of 8GB heap)
LIMIT_MB=7168

# Load project settings if available
if [ -f ".claude/.env" ]; then
    source .claude/.env
    LIMIT_MB=${CLAUDE_MEMORY_LIMIT_MB:-7168}
fi

# Find Claude Code process
CLAUDE_PID=$(pgrep -f "claude" | head -1)

if [ -z "$CLAUDE_PID" ]; then
    # No Claude process found, allow to continue
    exit 0
fi

# Get RSS (Resident Set Size) in KB
RSS_KB=$(ps -p $CLAUDE_PID -o rss= 2>/dev/null | awk '{print $1}')

if [ -z "$RSS_KB" ]; then
    # Could not get memory info, allow to continue
    exit 0
fi

# Convert to MB
RSS_MB=$((RSS_KB / 1024))

# Check against limit
if [ $RSS_MB -gt $LIMIT_MB ]; then
    echo -e "${RED}═══════════════════════════════════════════${NC}" >&2
    echo -e "${RED}🚨 MEMORY LIMIT EXCEEDED 🚨${NC}" >&2
    echo -e "${RED}═══════════════════════════════════════════${NC}" >&2
    echo -e "${RED}Current memory: ${RSS_MB}MB / ${LIMIT_MB}MB${NC}" >&2
    echo "" >&2
    echo -e "${YELLOW}This request has been BLOCKED to prevent crash${NC}" >&2
    echo "" >&2
    echo -e "${YELLOW}Action required:${NC}" >&2
    echo -e "${YELLOW}1. Start a new Claude Code session${NC}" >&2
    echo -e "${YELLOW}2. Your work is saved in git${NC}" >&2
    echo -e "${YELLOW}3. Context will reset to 0%${NC}" >&2
    echo -e "${RED}═══════════════════════════════════════════${NC}" >&2

    # Block the request
    exit 1
fi

# Memory is okay, allow to continue
exit 0
