#!/bin/bash
# Usage: ./bin/clean.sh [DIRECTORY]

DIR=${1:-downloads}

python -m src.main clean "$DIR"
