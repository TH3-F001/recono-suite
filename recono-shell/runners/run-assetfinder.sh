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

echo -e "⚡ Running AssetFinder against $DOMAINS..."
mkdir -p "$OUTPUT_DIR" || { echo "Failed to create directory: $OUTPUT_DIR"; exit 1; }

DOMAIN_LIST=($(comma_list_to_array "$DOMAINS"))

SUCCESS=true

for DOMAIN in "${DOMAIN_LIST[@]}"; do
    echo -e "\tRunning against $DOMAIN..."
    OUT_FILE="$OUTPUT_DIR/assetfinder_$DOMAIN.txt"
    assetfinder --subs-only "$DOMAIN" > "$OUT_FILE" &

done
wait
print_success "AssetFinder completed successfully"