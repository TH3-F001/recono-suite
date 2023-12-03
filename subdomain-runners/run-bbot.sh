#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-suite.lib"
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
BBOT_CMD="$BBOT -t $DOMAINS -f subdomain-enum --force --yes --silent --force --ignore-failed-deps -o $OUTPUT_DIR -rf"
[ "$active_mode" = true ] && BBOT_CMD+=" active" || BBOT_CMD+=" passive"

# Expect script
expect -c "
    spawn bash -c \"$BBOT_CMD\"
    set timeout -1
    expect {
        -re {.*: No events in queue} {
            send \"\r\"
            exp_continue
        }
        eof
    }
" > /dev/null

if [ $? -eq 0 ]; then 
    print_success "Bbot has completed successfully"
else 
    print_error "An error occurred while running Bbot"
fi
