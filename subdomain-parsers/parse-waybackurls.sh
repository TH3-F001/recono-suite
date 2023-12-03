#!/bin/bash
# set -e
# trap 'print_error "An error occured while parsing Assetfinder. Exiting..." >&2; exit 1' ERR

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
    print_error "parse-waybackurls.sh expects an input file, a comma separated domains list, and an output directory"
    echo "USAGE: parse-waybackurls.sh -i <input_file> -d <comma_separated_domains> -o <output_directory>"
    exit 1
fi

echo "🔍 Extracting WaybackUrls Domains: $DOMAINS From: $INPUT_DIR"


declare -a DOMAIN_ARRAY
comma_list_to_array "$DOMAINS" DOMAIN_ARRAY
HASH=$(hash_value "$DOMAINS,waybackurls")

TMP_DIR="/tmp/$HASH"
RESULT_DIR="/tmp/waybackurls_result_$HASH"
rm -rf "$TMP_DIR" "$RESULT_DIR"
mkdir -p "$TMP_DIR"
mkdir -p "$RESULT_DIR"

for DOMAIN in "${DOMAIN_ARRAY[@]}"; do
    for FILE in "$INPUT_DIR"/*"$DOMAIN"*; do
    
        if file_exists "$FILE"; then
            BASE_NAME=$(basename "$FILE")
            TMP_FILE="$TMP_DIR/$BASE_NAME"
            RESULT_FILE="$RESULT_DIR/$BASE_NAME"

            extract_domains_from_urls "$FILE" "$TMP_FILE"
            extract_target_domains "$TMP_FILE" "$DOMAINS" "$RESULT_FILE"
        else
            echo "$DOMAIN not found in $INPUT_DIR"
        fi
    done
done

OUT_FILE=$(join_subdomain_files "$DOMAINS" "$RESULT_DIR" "$OUTPUT_DIR" "waybackurls")

if file_exists "$OUT_FILE"; then
    print_success "WaybackUrls results successfuly extracted to $OUT_FILE"
else
    print_error "An error occurred while parsing WaybackUrls"
fi