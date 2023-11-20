#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"

echo -e "\n📦 Installing Subfinder..."
if ! command_exists subfinder; then
    INSTALL_COMMAND="go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    if ! generic_install_package "subfinder" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\t✨ Subfinder is already installed!"
fi