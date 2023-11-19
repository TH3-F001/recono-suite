#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"

echo "Installing AssetFinder..."
if ! command_exists assetfinder; then
    INSTALL_COMMAND="go install -v github.com/tomnomnom/assetfinder@latest"
    if ! generic_install_package "assetfinder" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\tAssetFinder is already installed!"
fi