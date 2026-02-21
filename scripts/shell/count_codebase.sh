#!/bin/bash

# Define the directory to search (defaults to current directory)
TARGET_PATH=$(realpath "${1:-.}")
TARGET_FOLDER=$(basename "$TARGET_PATH")
PARENT_FOLDER=$(basename "$(dirname "$TARGET_PATH")")

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${CYAN}🔍 Scanning for Python files (excluding migrations and venv)...${NC}"

# 1. Run the find and count
# 2. Grab the 'total' line (the last line)
# 3. Use awk to get just the number
TOTAL_RAW=$(find "$TARGET_PATH" \
    -path "*/migrations/*" -prune -o \
    -path "*/venv/*" -prune -o \
    -name "*.py" -print0 | xargs -0 wc -l | tail -n 1 | awk '{print $1}')

# Format number with thousand separator (works on most Linux/macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS version
    TOTAL_FORMATTED=$(printf "%'d" $TOTAL_RAW)
else
    # Linux version
    TOTAL_FORMATTED=$(echo $TOTAL_RAW | sed ':a;s/\b\([0-9]\+\)\([0-9]\{3\}\)\b/\1,\2/;ta')
fi

echo -e "------------------------------------------------------------"
echo -e "${BOLD}${PARENT_FOLDER}${NC} ➔  ${BOLD}${CYAN}${TARGET_FOLDER}${NC} houses exactly ${GREEN}${BOLD}${TOTAL_FORMATTED}${NC} lines of Python logic."
echo -e "------------------------------------------------------------"
