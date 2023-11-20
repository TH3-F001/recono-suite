#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"

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
