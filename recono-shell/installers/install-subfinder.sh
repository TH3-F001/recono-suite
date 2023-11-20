#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"

echo "Installing Subfinder..."
if ! command_exists subfinder; then
    INSTALL_COMMAND="go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    if ! generic_install_package "subfinder" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\tSubfinder is already installed!"
fi