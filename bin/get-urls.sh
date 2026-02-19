#!/bin/bash
# Usage: ./bin/get-urls.sh "API_URL" PAGE_FROM PAGE_TO [OUTPUT_FILE]

URL=$1
FROM=$2
TO=$3
OUTPUT=${4:-urls.txt}

if [ -z "$URL" ] || [ -z "$FROM" ] || [ -z "$TO" ]; then
    echo "Usage: $0 \"API_URL\" PAGE_FROM PAGE_TO [OUTPUT_FILE]"
    exit 1
fi

python -m src.main get-urls "$URL" "$FROM" "$TO" --output "$OUTPUT"
