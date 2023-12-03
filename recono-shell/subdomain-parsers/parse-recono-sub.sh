#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-shell.lib"
import_config_file

DOMAINS_=""
INPUT_DIR_=""
OUTPUT_DIR_=""

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -d|--domains) DOMAINS_="$2"; shift ;;
        -i|--input-dir) INPUT_DIR_="$2"; shift;;
        -o|--output) OUTPUT_DIR_="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if ! check_argument "$DOMAINS_" || ! check_argument "$INPUT_DIR_" || ! check_argument "$OUTPUT_DIR_"; then
    print_error "parse-recono-sub.sh expects a comma-separated list of domains, an input directory, and an output directory"
    echo "USAGE: parse-recono-sub.sh -d <domains> -i <input_directory> -o <output_directory>"
    exit 1
fi


echo "🔍 Extracting Recono-Sub Results On: $DOMAINS_ From: $INPUT_DIR_"
mkdir -p "$OUTPUT_DIR_" || { echo "Failed to create directory: $OUTPUT_DIR_"; exit 1; }
mkdir -p "$OUTPUT_DIR_/final_results" || { echo "Failed to create directory: $OUTPUT_DIR_/final_results"; exit 1; }
HASH=$(hash_value "$DOMAINS_,recono-sub")

"$SCRIPT_DIR/parse-amass.sh" -d "$DOMAINS_" -i "$INPUT_DIR_/amass/amass.sqlite" -o "$OUTPUT_DIR_/final_results"

"$SCRIPT_DIR/parse-c99.sh" -d "$DOMAINS_" -i "$INPUT_DIR_/c99" -o "$OUTPUT_DIR_/final_results"

"$SCRIPT_DIR/parse-crt.sh" -d "$DOMAINS_" -i "$INPUT_DIR_/crt.sh" -o "$OUTPUT_DIR_/final_results"

"$SCRIPT_DIR/parse-assetfinder.sh" -d "$DOMAINS_" -i "$INPUT_DIR_/assetfinder" -o "$OUTPUT_DIR_/final_results"

"$SCRIPT_DIR/parse-waybackurls.sh" -d "$DOMAINS_" -i "$INPUT_DIR_/waybackurls" -o "$OUTPUT_DIR_/final_results"

"$SCRIPT_DIR/parse-github-subdomains.sh" -d "$DOMAINS_" -i "$INPUT_DIR_/github-subdomains" -o "$OUTPUT_DIR_/final_results"

"$SCRIPT_DIR/parse-hakrawler.sh" -d "$DOMAINS_" -i "$INPUT_DIR_/hakrawler" -o "$OUTPUT_DIR_/final_results"

"$SCRIPT_DIR/parse-shosubgo.sh" -d "$DOMAINS_" -i "$INPUT_DIR_/shosubgo" -o "$OUTPUT_DIR_/final_results"

"$SCRIPT_DIR/parse-subdomainizer.sh" -d "$DOMAINS_" -i "$INPUT_DIR_/subdomainizer" -o "$OUTPUT_DIR_/final_results"

"$SCRIPT_DIR/parse-subfinder.sh" -d "$DOMAINS_" -i "$INPUT_DIR_/subfinder" -o "$OUTPUT_DIR_/final_results"

"$SCRIPT_DIR/parse-bbot.sh" -d "$DOMAINS_" -i "$INPUT_DIR_/bbot" -o "$OUTPUT_DIR_/final_results"

"$SCRIPT_DIR/parse-shuffledns.sh" -d "$DOMAINS_" -i "$INPUT_DIR_/shuffledns" -o "$OUTPUT_DIR_/final_results"

OUT_FILE=$(join_subdomain_files "$DOMAINS_" "$OUTPUT_DIR_/final_results" "$OUTPUT_DIR_" "recono-sub")
sort_subdomain_file "$OUT_FILE"
if file_exists "$OUT_FILE"; then
    print_success "Recono-Sub results successfuly extracted to $OUT_FILE"
    # cat "$OUT_FILE"
else
    print_error "An error occurred while parsing Recono-Sub"
fi
