#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"

echo -e "\n📦 Installing Bbot..."
if ! command_exists bbot; then
    INSTALL_COMMAND="pipx install bbot --force"
    if ! generic_install_package "bbot" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\t✨ Bbot is already installed!"
fi


