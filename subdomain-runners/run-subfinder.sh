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
    print_error "run-subfinder.sh requires -d (domains) and -o (output directory)"
    echo "USAGE: run-subfinder.sh -d <domains> -o <output_directory>"
    exit 1
fi

echo -e "⚡ Running Subfinder against $DOMAINS..."

mkdir -p "$OUTPUT_DIR"



HASH=$(hash_value "$DOMAINS,subfinder")
OUT_FILE="$OUTPUT_DIR/subfinder_$HASH.txt"

CMD="subfinder -d $DOMAINS -all -o $OUT_FILE -max-time 30"

if run_and_indent "$CMD" ; then 
    print_success "Subfinder has completed successfully"
else 
    print_error "An error occurred while running Subfinder"
fi

# $AUTORESPOND_SCRPT "$BBOT_CMD" "\[SUCC\] Scan ready\. Press enter to execute \w+" "\r"

