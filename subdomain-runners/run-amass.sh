#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-suite.lib"
import_config_file

DOMAINS=""
OUTPUT_DIR=""
active_mode=false

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -active) active_mode=true ;;
        -d|--domains) DOMAINS="$2"; shift ;;
        -o|--output) OUTPUT_DIR="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if ! check_argument "$DOMAINS" || ! check_argument "$OUTPUT_DIR"; then
    print_error "run-amass.sh expects a comma separated list of domains, and an output directory"
    echo "USAGE: run-amass.sh -d <domains> -o <output_directory> [-active]"
    exit 1
fi

echo -e "⚡ Running Amass against $DOMAINS..."

OUT_PRE=$(hash_value "$DOMAINS")
TRF=$TRUSTED_RESOLVER_FILE
UTRF=$UNTRUSTED_RESOLVER_FILE
DNSQPS=20                           # Total DNS Queries Per Second
URQPS=10                            # Total Untrusted DNS Queries Per Second
TRQPS=10                            # Total Trusted DNS Queries Per Second
LOG="$LOG_DIR/amass_$OUT_PRE.log"
mkdir -p "$OUTPUT_DIR"

AMASS_COMMAND="amass enum -d $DOMAINS -dns-qps $DNSQPS -log $LOG -dir $OUTPUT_DIR -silent"

if [ "$active_mode" = true ]; then
    AMASS_COMMAND+=" -active"
else
    AMASS_COMMAND+=" -passive"
fi

AMASS_COMMAND+=" -rf $UTRF -rqps $URQPS -trf $TRF -trqps $TRQPS"

if run_and_indent "$AMASS_COMMAND"; then
    print_success "Amass has completed successfully"
else
    print_error "An error occurred while running Amass"
fi