#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-suite.lib"
import_config_file

DOMAINS=""
OUTPUT_DIR=""

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -d|--domains) DOMAINS="$2"; shift ;;
        -o|--output) OUTPUT_DIR="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if ! check_argument "$DOMAINS" || ! check_argument "$OUTPUT_DIR"; then
    print_error "run-crt.sh requires -d (domains) and -o (output directory)"
    echo "USAGE: run-crt.sh -d <domains> -o <output_directory>"
    exit 1
fi

echo -e "⚡ Running Crt.sh against $DOMAINS..."
mkdir -p "$OUTPUT_DIR" || { echo "Failed to create directory: $OUTPUT_DIR"; exit 1; }

declare -a DOMAIN_LIST
comma_list_to_array "$DOMAINS" DOMAIN_LIST
CMDS=()

for DOMAIN in "${DOMAIN_LIST[@]}"; do
    echo -e "\tRunning against $DOMAIN..."
    OUT_FILE="$OUTPUT_DIR/crt.sh_$DOMAIN.txt"
    CMD="curl -s 'https://crt.sh/?q=$DOMAIN&output=json' | jq -r '.[].name_value' | sort -u > $OUT_FILE"
    CMDS+=("$CMD")
done

if run_async_commands "${CMDS[@]}"; then
    print_success "Crt.sh completed successfully"
else 
    print_error "An error occurred while running Crt.sh"
    exit 1
fi
