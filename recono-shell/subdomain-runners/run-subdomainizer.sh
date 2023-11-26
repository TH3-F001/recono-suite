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
CLOUD_FILE="$OUTPUT_DIR/subdomainizer_cloud_$OUT_PRE.txt"
URL_FILE=$(generate_url_list_from_domains "$DOMAINS")



CMD="subdomainizer -cop $CLOUD_FILE -d $DOMAINS -g -gt $GITHUB_API_KEY -o $OUT_FILE -san all -l $URL_FILE"

if run_and_indent "$CMD" ; then 
    print_success "SubdDomainizer has completed successfully"
else 
    print_error "An error occurred while running SubdDomainizer"
fi

# $AUTORESPOND_SCRPT "$BBOT_CMD" "\[SUCC\] Scan ready\. Press enter to execute \w+" "\r"

