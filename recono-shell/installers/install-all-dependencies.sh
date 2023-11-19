#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"


INITIAL_INSTALL_SCRIPT="$SCRIPT_DIR/install-root-dependencies.sh"
AMASS_INSTALL_SCRIPT="$SCRIPT_DIR/install-root"

check_and_run_script "$INITIAL_INSTALL_SCRIPT"


