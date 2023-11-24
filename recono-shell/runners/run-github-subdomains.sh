#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"

DOMAINS=$1
OUTPUT_DIR=$2

if ! check_argument "$DOMAINS" || ! check_argument "$OUTPUT_DIR"; then
    print_error "run-assetfinder-amass.sh expects a comma separated list of domains, and an output directory"
    exit 1
fi

echo -e "⚡ Running Github-Subdomains against $DOMAINS..."
mkdir -p "$OUTPUT_DIR" || { echo "Failed to create directory: $OUTPUT_DIR"; exit 1; }
