#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-shell.lib"
import_config_file

DOMAINS=$1
OUTPUT_DIR=$2

if ! check_argument "$DOMAINS" || ! check_argument "$OUTPUT_DIR"; then
    print_error "run-subdomainizer.sh expects a comma separated list of domains, and an output directory"
    exit 1
fi

echo -e "⚡ Running SubdDomainizer against $DOMAINS..."

mkdir -p "$OUTPUT_DIR"



OUT_PRE=$(hash_value "$DOMAINS")
OUT_FILE="$OUTPUT_DIR/subdomainizer_$OUT_PRE.txt"

CMD="subfinder -d $DOMAINS -all -o $OUT_FILE -max-time 30"

if run_and_indent "$CMD" ; then 
    print_success "SubdDomainizer has completed successfully"
else 
    print_error "An error occurred while running SubdDomainizer"
fi

# $AUTORESPOND_SCRPT "$BBOT_CMD" "\[SUCC\] Scan ready\. Press enter to execute \w+" "\r"

