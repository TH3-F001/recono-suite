#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-shell.lib"

DOMAINS="chinesehappiness.com,eastwindcomputers.com,lacity.gov"
OUTPUT_ROOT="$HOME/Downloads/recono-testing/results"

AMASS_OUT_DIR="$OUTPUT_ROOT/amass"
AMASS_SCRIPT="$SCRIPT_DIR/recon-tools/run-amass-passive.sh"

mkdir -p "$AMASS_OUT_DIR"

$AMASS_SCRIPT "$DOMAINS" "$AMASS_OUT_DIR"