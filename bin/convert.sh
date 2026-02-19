#!/bin/bash
# Usage: ./bin/convert.sh [TITLE] [AUTHOR] [COVER] [INPUT_DIR] [OUTPUT_FILE]

TITLE=${1:-"Wattpad Story"}
AUTHOR=${2:-"Unknown"}
COVER=${3:-"cover.png"}
INPUT=${4:-"downloads"}
OUTPUT=$5

if [ -z "$OUTPUT" ]; then
    python -m src.main convert --title "$TITLE" --author "$AUTHOR" --cover "$COVER" --input "$INPUT"
else
    python -m src.main convert --title "$TITLE" --author "$AUTHOR" --cover "$COVER" --input "$INPUT" --output "$OUTPUT"
fi
