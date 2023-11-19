#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"

echo "Installing Shosubgo..."
if ! command_exists shosubgo; then
    INSTALL_COMMAND="go install github.com/incogbyte/shosubgo@latest"
    if ! generic_install_package "shosubgo" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\tShosubgo is already installed!"
fi