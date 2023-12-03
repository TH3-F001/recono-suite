#!/bin/bash


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"

DB_FILE=""
OUTPUT_DIR=""
DOMAINS=""

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -i|--input) DB_FILE="$2"; shift ;;
        -o|--output) OUTPUT_DIR="$2"; shift ;;
        -d|--domains) DOMAINS=$2; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if ! check_argument "$DB_FILE" || ! check_argument "$OUTPUT_DIR" || ! check_argument "$DOMAINS"; then
    print_error "parse-amass.sh expects an input file, a comma separated domains list, and an output directory"
    echo "USAGE: parse-amass.sh -i <input_file> -d <comma_separated_domains> -o <output_directory>"
    exit 1
fi

SQLITE=""
if command_exists sqlite3; then
    SQLITE=sqlite3
elif command_exists sqlite2; then
    SQLITE=sqlite2
elif command_exists sqlite1; then
    SQLITE=sqlite
else
    print_error "no versions of sqlite found. please install sqlite3 and try again."
fi

echo "🔍 Extracting Amass Domains: $DOMAINS from $DB_FILE"

HASH=$(hash_value "$DOMAINS,amass")
TMP_FILE="/tmp/parse_$HASH.tmp"
declare -a DOMAIN_ARRAY
comma_list_to_array "$DOMAINS" DOMAIN_ARRAY
OUT_FILE="$OUTPUT_DIR/amass_parsed_$HASH.txt"

$SQLITE "$DB_FILE" "SELECT content FROM assets WHERE type='FQDN';" > "$TMP_FILE"

grep -oP '"name":"\K[^"]+' "$TMP_FILE" | while read -r EXTRACTED_DOMAIN; do
    for DOMAIN in "${DOMAIN_ARRAY[@]}"; do
        if [[ "$EXTRACTED_DOMAIN" == *"$DOMAIN"* ]]; then
            echo "$EXTRACTED_DOMAIN" >> "$OUT_FILE"
            break
        fi
    done
done

sort_subdomain_file "$OUT_FILE" > "$TMP_FILE"
uniq "$TMP_FILE" > "$OUT_FILE"

if file_exists "$OUT_FILE"; then
    print_success "Amass results successfuly extracted to $OUT_FILE"
else
    print_error "An error occurred while parsing Amass"
fi
