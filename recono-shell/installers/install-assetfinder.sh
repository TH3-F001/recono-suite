#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"

echo -e "\n📦 Installing AssetFinder..."
if ! command_exists assetfinder; then
    INSTALL_COMMAND="go install -v github.com/tomnomnom/assetfinder@latest"
    if ! generic_install_package "assetfinder" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\t✨ AssetFinder is already installed!"
fi