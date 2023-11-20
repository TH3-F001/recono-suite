#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-shell.lib"
import_config_file

#Expects to be either a single domain or comma-separated list
DOMAINS=$1
OUTPUT_DIR=$2

if ! check_argument "$DOMAINS" || ! check_argument "$OUTPUT_DIR"; then
    print_error "run-passive-amass.sh expects a comma separated list of domains, and an output directory"
    exit 1
fi

echo -e "⚡ Running Amass against $DOMAINS..."

OUT_PRE=$(hash_value "$DOMAINS")
TRF=$TRUSTED_RESOLVER_FILE
UTRF=$UNTRUSTED_RESOLVER_FILE
DNSQPS=20                           # Total DNS Queries Per Second
URQPS=10                            # Total Untrusted DNS Queries Per Second
TRQPS=10                            # Total Trusted DNS Queries Per Second
LOG="$LOG_DIR/amass_passive_$OUT_PRE.log"
mkdir -p "$OUTPUT_DIR"

run_and_indent amass enum -d "$DOMAINS" -dns-qps "$DNSQPS" -log "$LOG" -oA "$OUT_PRE" -dir "$OUTPUT_DIR" -passive -rf "$UTRF" -rqps "$URQPS" -trf "$TRF" -trqps "$TRQPS"