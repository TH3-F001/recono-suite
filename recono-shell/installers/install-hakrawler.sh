#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"

echo -e "\n📦 Installing Hakrawler..."
if ! command_exists hakrawler; then
    INSTALL_COMMAND="go install -v github.com/hakluke/hakrawler@latest"
    if ! generic_install_package "hakrawler" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\t✨ Hakrawler is already installed!"
fi