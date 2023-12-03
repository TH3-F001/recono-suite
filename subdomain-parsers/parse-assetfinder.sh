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
    print_error "parse-assetfinder.sh expects an input file, a comma separated domains list, and an output directory"
    echo "USAGE: parse-assetfinder.sh -i <input_file> -d <comma_separated_domains> -o <output_directory>"
    exit 1
fi

echo "🔍 Extracting Assetfinder Domains: $DOMAINS From: $INPUT_DIR"

OUT_FILE=$(join_subdomain_files "$DOMAINS" "$INPUT_DIR" "$OUTPUT_DIR" "assetfinder")

if file_exists "$OUT_FILE"; then
    print_success "Assetfinder results successfuly extracted to $OUT_FILE"
else
    print_error "An error occurred while parsing Assetfinder"
fi