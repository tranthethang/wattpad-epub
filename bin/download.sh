#!/bin/bash
# Usage: ./bin/download.sh [URLS_FILE] [OUTPUT_DIR] [CONCURRENCY]

URLS=${1:-urls.txt}
OUTPUT=${2:-downloads}
CONCURRENCY=${3:-4}

if [ ! -f "$URLS" ]; then
    echo "Error: URLs file '$URLS' not found."
    exit 1
fi

python -m src.main download "$URLS" --output "$OUTPUT" --concurrency "$CONCURRENCY"
