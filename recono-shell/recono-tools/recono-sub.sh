#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"
RUNNER_DIR="$SCRIPT_DIR/../subdomain-runners"
PARSER_DIR="$SCRIPT_DIR/../subdomain-parsers"
source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-shell.lib"
import_config_file

_DOMAIN_FILE_=""
_OUT_DIR_=""
_ACTIVE_MODE_=false
_CHUNK_SIZE_=10  # Adjust this to tune speed-resource availability ratio

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -active) _ACTIVE_MODE_=true ;;
        -d|--domain-file) _DOMAIN_FILE_="$2"; shift ;;
        -o|--output) _OUT_DIR_="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if ! check_argument "$_DOMAIN_FILE_" || ! check_argument "$_OUT_DIR_"; then
    print_error "recono-sub.sh expects a domain file and an output directory"
    echo "USAGE: recono-sub.sh -d <domain_file> -o <output_directory> [-active]"
    exit 1
fi

echo -e "⚡ Running Recono-Sub against domains from $_DOMAIN_FILE_..."
mkdir -p "$_OUT_DIR_" || { echo "Failed to create directory: $_OUT_DIR_"; exit 1; }

# Function to process chunks of domains
process_chunk() {
    local DOMAINS_CHUNK="$1"
    local OUT_DIR="$2"
    local ACTIVE_FLAG="$3"

    if [ "$ACTIVE_FLAG" = true ]; then
        "$RUNNER_DIR/run-recono-sub.sh" -d "$DOMAINS_CHUNK" -o "$OUT_DIR" -active
    else
        "$RUNNER_DIR/run-recono-sub.sh" -d "$DOMAINS_CHUNK" -o "$OUT_DIR"
    fi
}

# Read domains from file and chunk them
# IFS=$'\n' read -d '' -r -a _DOMAINS_ < "$_DOMAIN_FILE_"
# for ((i=0; i<${#_DOMAINS_[@]}; i+=_CHUNK_SIZE_)); do
#     _CHUNK_=$(IFS=,; echo "${_DOMAINS_[*]:i:_CHUNK_SIZE_}")
#     process_chunk "$_CHUNK_" "$_OUT_DIR_" "$_ACTIVE_MODE_"
# done

_DOMAINS_=$(file_to_comma_list "$_DOMAIN_FILE_") 
_OUT_FILE_=$("$PARSER_DIR/parse-recono-sub.sh" -d "$_DOMAINS_" -i "$_OUT_DIR_" -o "$_OUT_DIR_" )
cat "$_OUT_FILE_"