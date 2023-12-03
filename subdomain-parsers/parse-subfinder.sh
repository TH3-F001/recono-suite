#!/bin/bash


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"

INPUT_DIR=""
OUTPUT_DIR=""
DOMAINS=""

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -i|--input) INPUT_DIR="$2"; shift ;;
        -o|--output) OUTPUT_DIR="$2"; shift ;;
        -d|--domains) DOMAINS=$2; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if ! check_argument "$INPUT_DIR" || ! check_argument "$OUTPUT_DIR" || ! check_argument "$DOMAINS"; then
    print_error "parse-subfinder.sh expects an input file, a comma separated domains list, and an output directory"
    echo "USAGE: parse-subfinder.sh -i <input_file> -d <comma_separated_domains> -o <output_directory>"
    exit 1
fi

echo "🔍 Extracting Subfinder Domains: $DOMAINS From: $INPUT_DIR"

HASH=$(hash_value "$DOMAINS,subfinder")
OUT_FILE="$OUTPUT_DIR/subfinder_parsed_$HASH.txt"
declare -a DOMAIN_ARRAY
comma_list_to_array "$DOMAINS" DOMAIN_ARRAY
echo "" > "$OUT_FILE"

for FILE in "$INPUT_DIR"/*; do
    if file_exists "$FILE" && [[ "$FILE" != "$OUT_FILE" ]]; then
        for DOMAIN in "${DOMAIN_ARRAY[@]}"; do
            grep "$DOMAIN" "$FILE" >> "$OUT_FILE"
        done
    fi
done

sort_subdomain_file "$OUT_FILE" > "/tmp/$HASH.tmp"

uniq "/tmp/$HASH.tmp" > "$OUT_FILE"

if file_exists "$OUT_FILE"; then
    print_success "Subfinder results successfuly extracted to $OUT_FILE" 
else
    print_error "An error occurred while parsing Subfinder"
fi