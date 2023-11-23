#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"

echo "Installing WaybackURLs..."
if ! command_exists waybackurls; then
    INSTALL_COMMAND="go install -v github.com/tomnomnom/waybackurls@latest"
    if ! generic_install_package "waybackurls" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\tWaybackURLs is already installed!"
fi