#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-suite.lib"
import_config_file

DOMAINS=""
OUTPUT_DIR=""
active_mode=false
TIMEOUT_MODIFIER=1

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
BBOT_CMD="$BBOT -t $DOMAINS -f subdomain-enum --yes --silent --force --ignore-failed-deps -o $OUTPUT_DIR -rf"

if [ "$active_mode" = true ]; then
    BBOT_CMD+=" active"
    TIMEOUT_MODIFIER=$(echo "$TIMEOUT_MODIFIER * 1.5" | bc)
else
    BBOT_CMD+=" passive"
fi

# We add a timeout, again because bbot kinda sucks... but it finds a lot of domains so...
HASH=$(hash_value "$DOMAINS,bbot")
BBOT_SESSION="bbot_$HASH"
declare -a DOM_ARR
comma_list_to_array "$DOMAINS" DOM_ARR
DOMAIN_COUNT=${#DOM_ARR[@]}
TOTAL_TIMEOUT=$(printf "%.0f" $(echo "$DOMAIN_COUNT * 3600 * $TIMEOUT_MODIFIER" | bc))

# We use tmux because bbot poorly handles stdout, and sometimes waits for user input when it shouldnt
tmux_command_with_timeout "$BBOT_CMD" "$TOTAL_TIMEOUT" "$BBOT_SESSION"
BBOT_EXIT_STATUS=$?



if [ "$BBOT_EXIT_STATUS" -eq 0 ]; then 
    print_success "Bbot has completed successfully"
else 
    print_error "An error occurred while running Bbot"
fi

