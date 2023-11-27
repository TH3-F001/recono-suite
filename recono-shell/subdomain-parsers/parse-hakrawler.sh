#!/bin/bash
set -e
trap 'print_error "An error occured while parsing Assetfinder. Exiting..." >&2; exit 1' ERR

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
    print_error "parse-hakrawler.sh expects an input file, a comma separated domains list, and an output directory"
    echo "USAGE: parse-hakrawler.sh -i <input_file> -d <comma_separated_domains> -o <output_directory>"
    exit 1
fi

echo "🔍 Extracting Hakrawler Domains: $DOMAINS From: $INPUT_DIR"


declare -a DOMAIN_ARRAY
comma_list_to_array "$DOMAINS" DOMAIN_ARRAY
HASH=$(hash_value "$DOMAINS,hakrawler")

mkdir -p "/tmp/$HASH"
for DOMAIN in "${DOMAIN_ARRAY[@]}"; do
    for FILE in "$INPUT_DIR"/*"$DOMAIN"*; do
        if file_exists "$FILE"; then
            BASE=$(basename "$FILE")
            TMP_FILE="/tmp/$HASH/$BASE"
            extract_domains_from_urls "$FILE" "$TMP_FILE"
            echo "$TMP_FILE"
            extract_target_domains "$TMP_FILE" DOMAIN_ARRAY "$TMP_FILE.extracted"
            cat "$TMP_FILE.extracted" > "$TMP_FILE"
        else
            echo "WTF?"
        fi
    done
done
echo TEST

OUT_FILE=$(join_subdomain_files "$DOMAINS" "/tmp/$HASH" "/tmp" "hakrawler")
echo "/tmp/$HASH"

if file_exists "$OUT_FILE"; then
    print_success "Hakrawler results successfuly extracted to $OUT_FILE"
else
    print_error "An error occurred while parsing Hakrawler"
fi