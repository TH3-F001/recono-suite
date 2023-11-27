#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"

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
    print_error "run-waybackurls.sh requires -d (domains) and -o (output directory)"
    echo "USAGE: run-waybackurls.sh -d <domains> -o <output_directory>"
    exit 1
fi

echo -e "⚡ Running WaybackUrls against $DOMAINS..."
mkdir -p "$OUTPUT_DIR" || { echo "Failed to create directory: $OUTPUT_DIR"; exit 1; }

declare -a DOMAIN_LIST
comma_list_to_array "$DOMAINS" DOMAIN_LIST
CMDS=()

for DOMAIN in "${DOMAIN_LIST[@]}"; do
    echo -e "\tRunning against $DOMAIN..."
    OUT_FILE="$OUTPUT_DIR/waybackurls_$DOMAIN.txt"
    CMD="echo '$DOMAIN' | waybackurls > $OUT_FILE"
    CMDS+=("$CMD")
done

if run_async_commands "${CMDS[@]}"; then
    print_success "WaybackUrls completed successfully"
else 
    print_error "An error occurred while running WaybackUrls"
    exit 1
fi
