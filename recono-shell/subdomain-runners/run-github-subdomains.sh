#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
import_config_file

DOMAINS=$1
OUTPUT_DIR=$2

if ! check_argument "$DOMAINS" || ! check_argument "$OUTPUT_DIR"; then
    print_error "run-github-subdomains.sh expects a comma separated list of domains, and an output directory"
    exit 1
fi

echo -e "⚡ Running Github-Subdomains against $DOMAINS..."
mkdir -p "$OUTPUT_DIR" || { echo "Failed to create directory: $OUTPUT_DIR"; exit 1; }

DOMAIN_LIST=($(comma_list_to_array "$DOMAINS"))
CMDS=()

for DOMAIN in "${DOMAIN_LIST[@]}"; do
    echo -e "\tRunning against $DOMAIN..."
    REG_OUT_FILE="$OUTPUT_DIR/github-subdomains_$DOMAIN.txt"
    EXT_OUT_FILE="$OUTPUT_DIR/github-subdomains_ext_$DOMAIN.txt"
    RAW_OUT_FILE="$OUTPUT_DIR/github-subdomains_raw_$DOMAIN.txt"
    REG_CMD="github-subdomains -d $DOMAIN -o $REG_OUT_FILE -t $GITHUB_API_KEY 1> /dev/null"
    EXT_CMD="github-subdomains -d $DOMAIN -e -o $EXT_OUT_FILE -t $GITHUB_API_KEY 1> /dev/null"
    RAW_CMD="github-subdomains -d $DOMAIN -raw -o $RAW_OUT_FILE -t $GITHUB_API_KEY 1> /dev/null"
    CMDS+=("$REG_CMD" "$EXT_CMD" "$RAW_CMD")
done

if run_async_commands "${CMDS[@]}" & display_hacky_animation ; then
    print_success "Github-Subdomains completed successfully"
else 
    print_error "An error occurred while running Github-Subdomains"
    exit 1
fi

