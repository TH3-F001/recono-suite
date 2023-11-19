#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"

echo "Installing Bbot..."
if ! command_exists bbot; then
    INSTALL_COMMAND="pipx install bbot --force"
    if ! generic_install_package "bbot" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\tBbot is already installed!"
fi
