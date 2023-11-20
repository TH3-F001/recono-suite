#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"

echo -e "\n📦 Installing WaybackURLs..."
if ! command_exists waybackurls; then
    INSTALL_COMMAND="go install -v github.com/tomnomnom/waybackurls@latest"
    if ! generic_install_package "waybackurls" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\t✨ WaybackURLs is already installed!"
fi