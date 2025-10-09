#!/bin/bash
# Variable Injection for Slash Commands
# Replaces $VARIABLE placeholders in slash command prompts with actual values

set -e

COMMAND_FILE="$1"
VARIABLES_FILE=".claude/.variables.json"

# Check if variables file exists
if [ ! -f "$VARIABLES_FILE" ]; then
    # Create default variables file
    cat > "$VARIABLES_FILE" <<'EOF'
{
  "TASK": "",
  "FILE_LIST": "",
  "PLAN_PATH": "",
  "REVIEW_REPORT": "",
  "CURRENT_STEP": "scout",
  "WORKFLOW_STATUS": "idle",
  "MODIFIED_FILES": [],
  "CURRENT_AGENT": "",
  "FIX_ATTEMPTS": 0,
  "LAST_UPDATED": ""
}
EOF
fi

# Read variables from JSON file
if command -v jq &> /dev/null; then
    TASK=$(jq -r '.TASK // ""' "$VARIABLES_FILE")
    FILE_LIST=$(jq -r '.FILE_LIST // ""' "$VARIABLES_FILE")
    PLAN_PATH=$(jq -r '.PLAN_PATH // ""' "$VARIABLES_FILE")
    REVIEW_REPORT=$(jq -r '.REVIEW_REPORT // ""' "$VARIABLES_FILE")
    CURRENT_STEP=$(jq -r '.CURRENT_STEP // "scout"' "$VARIABLES_FILE")
    CURRENT_AGENT=$(jq -r '.CURRENT_AGENT // ""' "$VARIABLES_FILE")
else
    # Fallback if jq not available - just pass through
    TASK=""
    FILE_LIST=""
    PLAN_PATH=""
    REVIEW_REPORT=""
    CURRENT_STEP="scout"
    CURRENT_AGENT=""
fi

# Read command file content
COMMAND_CONTENT=$(cat "$COMMAND_FILE")

# Perform variable substitution
COMMAND_CONTENT=$(echo "$COMMAND_CONTENT" | sed \
    -e "s|\\\$TASK|$TASK|g" \
    -e "s|\\\$FILE_LIST|$FILE_LIST|g" \
    -e "s|\\\$PLAN_PATH|$PLAN_PATH|g" \
    -e "s|\\\$REVIEW_REPORT|$REVIEW_REPORT|g" \
    -e "s|\\\$CURRENT_STEP|$CURRENT_STEP|g" \
    -e "s|\\\$CURRENT_AGENT|$CURRENT_AGENT|g")

# Output the modified content
echo "$COMMAND_CONTENT"

exit 0
