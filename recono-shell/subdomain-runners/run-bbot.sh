#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-shell.lib"
import_config_file

DOMAINS=""
OUTPUT_DIR=""
active_mode=false

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -active) active_mode=true ;;
        -d|--domains) DOMAINS="$2"; shift ;;
        -o|--output) OUTPUT_DIR="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if ! check_argument "$DOMAINS" || ! check_argument "$OUTPUT_DIR"; then
    print_error "run-bbot.sh expects a comma separated list of domains, and an output directory"
    echo "USAGE: run-bbot.sh -d <domains> -o <output_directory> [-active]"

    exit 1
fi

echo -e "⚡ Running Bbot against $DOMAINS..."

mkdir -p "$OUTPUT_DIR"

BBOT=$(which bbot)
BBOT_CMD="$BBOT -t $DOMAINS -f subdomain-enum --force --yes --silent --ignore-failed-deps -o $OUTPUT_DIR -rf 1> /dev/null"

if [ "$active_mode" = true ]; then
    BBOT_CMD+=" active"
else
    BBOT_CMD+=" passive"
fi

if run_and_indent "$BBOT_CMD" ; then 
    print_success "Bbot has completed successfully"
else 
    print_error "An error occurred while running Bbot"
fi

# $AUTORESPOND_SCRPT "$BBOT_CMD" "\[SUCC\] Scan ready\. Press enter to execute \w+" "\r"

