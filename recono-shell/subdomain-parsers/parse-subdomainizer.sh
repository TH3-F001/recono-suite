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
    print_error "parse-subdomainizer.sh expects an input file, a comma separated domains list, and an output directory"
    echo "USAGE: parse-subdomainizer.sh -i <input_file> -d <comma_separated_domains> -o <output_directory>"
    exit 1
fi

echo "🔍 Extracting SubDomainizer Domains: $DOMAINS From: $INPUT_DIR"
HASH=$(hash_value "$DOMAINS,subdomainizer")
CLOUD_DIR="/tmp/cloud_$HASH"
REG_DIR="/tmp/reg_$HASH"
rm -rf "$CLOUD_DIR" "$REG_DIR"
mkdir -p "$CLOUD_DIR"
mkdir -p "$REG_DIR"

for FILE in "$INPUT_DIR"/*; do
    if file_exists "$FILE" && [[ "$FILE" == *"$HASH"* ]]; then
        if [[ "$FILE" == *"cloud"* ]]; then
            cp -r "$FILE" "$CLOUD_DIR"
        else
            cp -r "$FILE" "$REG_DIR"
        fi
    fi
done

OUT_FILE=$(join_subdomain_files "$HASH" "$REG_DIR" "$OUTPUT_DIR" "subdomainizer")

for FILE in "$CLOUD_DIR"/*; do
    if file_exists $FILE; then
        cat "$FILE" >> "$OUT_FILE"
    fi
done

if file_exists "$OUT_FILE"; then
    print_success "SubDomainizer results successfuly extracted to $OUT_FILE"
else
    print_error "An error occurred while parsing SubDomainizer"
fi