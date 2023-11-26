#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
import_config_file

DOMAINS=$1
OUTPUT_DIR=$2

if ! check_argument "$DOMAINS" || ! check_argument "$OUTPUT_DIR"; then
    print_error "run-shuffledns.sh expects a comma separated list of domains, and an output directory"
    exit 1
fi

echo -e "⚡ Running ShuffleDns against $DOMAINS..."
mkdir -p "$OUTPUT_DIR" || { echo "Failed to create directory: $OUTPUT_DIR"; exit 1; }

DOMAIN_LIST=($(comma_list_to_array "$DOMAINS"))
CMDS=()

for DOMAIN in "${DOMAIN_LIST[@]}"; do
    echo -e "\tRunning against $DOMAIN..."
    OUT_FILE="$OUTPUT_DIR/shuffledns_$DOMAIN.txt"
    CMD="shuffledns -d $DOMAIN -w $SUBDOMAIN_MASTER_LIST -r $TRUSTED_RESOLVER_FILE -t 1000 -o $OUT_FILE"
    CMDS+=("$CMD")
done

if run_async_commands "${CMDS[@]}"; then
    print_success "ShuffleDns completed successfully"
else 
    print_error "An error occurred while running ShuffleDns"
    exit 1
fi
