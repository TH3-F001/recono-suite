#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"

echo -e "\n📦 Installing Shosubgo..."
if ! command_exists shosubgo; then
    INSTALL_COMMAND="go install github.com/incogbyte/shosubgo@latest"
    if ! generic_install_package "shosubgo" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\t✨ Shosubgo is already installed!"
fi