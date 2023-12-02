#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-shell.lib"
import_config_file

DOMAINS_=""
OUTPUT_DIR_=""
active_mode_=false

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -active) active_mode_=true ;;
        -d|--domains) DOMAINS_="$2"; shift ;;
        -o|--output) OUTPUT_DIR_="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if ! check_argument "$DOMAINS_" || ! check_argument "$OUTPUT_DIR_"; then
    print_error "run-recono-sub.sh expects a comma separated list of domains, and an output directory"
    echo "USAGE: run-recono-sub.sh -d <domains> -o <output_directory> [-active]"
    exit 1
fi

echo -e "⚡ Running Recono-Sub against $DOMAINS_..."
mkdir -p "$OUTPUT_DIR_" || { echo "Failed to create directory: $OUTPUT_DIR_"; exit 1; }



if [ "$active_mode_" = true ]; then
    "$SCRIPT_DIR/run-amass.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/amass" -active &
else
    "$SCRIPT_DIR/run-amass.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/amass" &
fi

PID=$!
sleep 1
"$SCRIPT_DIR/run-c99.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/c99" &
sleep 1
"$SCRIPT_DIR/run-crt.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/crt.sh" &
sleep 1
"$SCRIPT_DIR/run-assetfinder.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/assetfinder" &
sleep 1
"$SCRIPT_DIR/run-waybackurls.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/waybackurls" &
sleep 1
"$SCRIPT_DIR/run-github-subdomains.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/github-subdomains"&
sleep 1
"$SCRIPT_DIR/run-hakrawler.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/hakrawler"&
sleep 1
"$SCRIPT_DIR/run-shosubgo.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/shosubgo"&
sleep 1
"$SCRIPT_DIR/run-subdomainizer.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/subdomainizer"&
wait $PID
"$SCRIPT_DIR/run-subfinder.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/subfinder"

if [ "$active_mode_" = true ]; then
    "$SCRIPT_DIR/run-bbot.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/bbot" -active
else
    "$SCRIPT_DIR/run-bbot.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/bbot"
fi

"$SCRIPT_DIR/run-shuffledns.sh" -d "$DOMAINS_" -o "$OUTPUT_DIR_/shuffledns"