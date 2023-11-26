#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"

DOMAINS=$1
OUTPUT_DIR=$2

if ! check_argument "$DOMAINS" || ! check_argument "$OUTPUT_DIR"; then
    print_error "run-hakrawler.sh expects a comma separated list of domains, and an output directory"
    exit 1
fi

echo -e "⚡ Running Hakrawler against $DOMAINS..."
mkdir -p "$OUTPUT_DIR" || { echo "Failed to create directory: $OUTPUT_DIR"; exit 1; }

DOMAIN_LIST=($(comma_list_to_array "$DOMAINS"))
CMDS=()

for DOMAIN in "${DOMAIN_LIST[@]}"; do
    echo -e "\tRunning against $DOMAIN..."
    OUT_FILE="$OUTPUT_DIR/hakrawler_$DOMAIN.txt"
    URL="http://$DOMAIN"
    CMD="echo '$URL' | hakrawler -d 5 -subs $DOMAIN -u > $OUT_FILE"
    CMDS+=("$CMD")
done

if run_async_commands "${CMDS[@]}"; then
    print_success "Hakrawler completed successfully"
else 
    print_error "An error occurred while running Hakrawler"
    exit 1
fi
