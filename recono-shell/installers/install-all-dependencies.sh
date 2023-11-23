#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"


declare -a INSTALLER_SCRIPTS=(
"$SCRIPT_DIR/install-root-dependencies.sh"
"$SCRIPT_DIR/install-amass.sh"
"$SCRIPT_DIR/install-assetfinder.sh"
"$SCRIPT_DIR/install-bbot.sh"
"$SCRIPT_DIR/install-github-subdomains.sh"
"$SCRIPT_DIR/install-hakrawler.sh"
"$SCRIPT_DIR/install-knockpy.sh"
"$SCRIPT_DIR/install-shosubgo.sh"
"$SCRIPT_DIR/install-shuffledns.sh"
"$SCRIPT_DIR/install-subdomainizer.sh"
"$SCRIPT_DIR/install-subfinder.sh"
"$SCRIPT_DIR/install-waybackurls.sh"
)

for SCRIPT in "${INSTALLER_SCRIPTS[@]}"; do
    check_and_run_script "$SCRIPT"
done
