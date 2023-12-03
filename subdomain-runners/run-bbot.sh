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
BBOT_CMD="$BBOT -t $DOMAINS -f subdomain-enum --yes --silent --force --ignore-failed-deps -o $OUTPUT_DIR -rf"
[ "$active_mode" = true ] && BBOT_CMD+=" active" || BBOT_CMD+=" passive"

echo $BBOT_CMD

# We use tmux because bbot poorly handles stdout, and sometimes waits for user input when it shouldnt
echo -e "\tStarting tmux session with bbot command..."
tmux new-session -d -s bbot_session "bash -c '$BBOT_CMD; echo \$? > /tmp/bbot_exit_status'"

while true; do
    if ! pgrep -f "$BBOT_CMD" > /dev/null; then
        echo "Bbot command finished. Exiting loop..."
        break
    fi
    tmux send-keys -t bbot_session Enter
    sleep 10
done

tmux kill-session -t bbot_session

BBOT_EXIT_STATUS=$(cat /tmp/bbot_exit_status)
rm /tmp/bbot_exit_status



if [ "$BBOT_EXIT_STATUS" -eq 0 ]; then 
    print_success "Bbot has completed successfully"
else 
    print_error "An error occurred while running Bbot"
fi

