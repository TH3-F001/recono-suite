#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"
RUNNER_DIR="$SCRIPT_DIR/../subdomain-runners"
PARSER_DIR="$SCRIPT_DIR/../subdomain-parsers"
source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-shell.lib"
import_config_file

DOMAIN_FILE=""
OUTPUT_DIR=""
ACTIVE_MODE=false
CHUNK_SIZE=10  # AAjust this to tune speed-resource availability ratio

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -active) ACTIVE_MODE=true ;;
        -d|--domain-file) DOMAIN_FILE="$2"; shift ;;
        -o|--output) OUTPUT_DIR="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if ! check_argument "$DOMAIN_FILE" || ! check_argument "$OUTPUT_DIR"; then
    print_error "recono-sub.sh expects a domain file and an output directory"
    echo "USAGE: recono-sub.sh -d <domain_file> -o <output_directory> [-active]"
    exit 1
fi

echo -e "⚡ Running Recono-Sub against domains from $DOMAIN_FILE..."
mkdir -p "$OUTPUT_DIR" || { echo "Failed to create directory: $OUTPUT_DIR"; exit 1; }

# Function to process chunks of domains
process_chunk() {
    local DOMAINS_CHUNK="$1"
    local OUTPUT_DIR="$2"
    local ACTIVE_FLAG="$3"

    if [ "$ACTIVE_FLAG" = true ]; then
        "$RUNNER_DIR/run-recono-sub.sh" -d "$DOMAINS_CHUNK" -o "$OUTPUT_DIR" -active
    else
        "$RUNNER_DIR/run-recono-sub.sh" -d "$DOMAINS_CHUNK" -o "$OUTPUT_DIR"
    fi
}

# Read domains from file and chunk them
IFS=$'\n' read -d '' -r -a _DOMAINS < "$DOMAIN_FILE"
for ((i=0; i<${#_DOMAINS[@]}; i+=CHUNK_SIZE)); do
    CHUNK=$(IFS=,; echo "${_DOMAINS[*]:i:CHUNK_SIZE}")
    process_chunk "$CHUNK" "$OUTPUT_DIR/amass" "$ACTIVE_MODE"
    echo "$CHUNK"
done
