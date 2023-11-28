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
    print_error "parse-bbot.sh expects an input file, a comma separated domains list, and an output directory"
    echo "USAGE: parse-bbot.sh -i <input_file> -d <comma_separated_domains> -o <output_directory>"
    exit 1
fi

echo "🔍 Extracting Bbot Domains: $DOMAINS From: $INPUT_DIR"

SUBDOMAIN_FILENAME="subdomains.txt"
HASH=$(hash_value "$DOMAINS,bbot")
TMP_FILE="/tmp/bbot_$HASH"
OUT_FILE="${OUTPUT_DIR}/bbot_parsed_${HASH}.txt"
declare -a DOMAIN_ARRAY
comma_list_to_array "$DOMAINS" DOMAIN_ARRAY

find "$INPUT_DIR" -type f -name "$SUBDOMAIN_FILENAME" | while read -r FILE; do
    for DOMAIN in "${DOMAIN_ARRAY[@]}"; do 
        if grep -q "$DOMAIN" "$FILE"; then
            cat "$FILE" >> "$OUT_FILE"
            break
        fi
        echo $DOMAIN
    done
done

sort_subdomain_file "$OUT_FILE" > "$TMP_FILE"
uniq "$TMP_FILE" > "$OUT_FILE"

if file_exists "$OUT_FILE"; then
    print_success "Bbot results successfuly extracted to $OUT_FILE"
else
    print_error "An error occurred while parsing Bbot"
fi

