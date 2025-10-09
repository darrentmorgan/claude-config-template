#!/bin/bash
# Update Variables After Slash Command Execution
# Updates .claude/.variables.json with new state

set -e

VARIABLES_FILE=".claude/.variables.json"

# Get parameters
KEY="$1"
VALUE="$2"

# Ensure variables file exists
if [ ! -f "$VARIABLES_FILE" ]; then
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

# Update the variable using jq
if command -v jq &> /dev/null; then
    # Update timestamp
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Update the key and timestamp
    jq --arg key "$KEY" --arg value "$VALUE" --arg ts "$TIMESTAMP" \
        '.[$key] = $value | .LAST_UPDATED = $ts' \
        "$VARIABLES_FILE" > "${VARIABLES_FILE}.tmp"

    mv "${VARIABLES_FILE}.tmp" "$VARIABLES_FILE"

    echo "✓ Updated $KEY = $VALUE"
else
    echo "⚠️  jq not installed - variable update skipped"
fi

exit 0
