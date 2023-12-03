#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"

echo -e "\n📦 Installing Amass..."
if ! command_exists amass; then
    INSTALL_COMMAND="go install -v github.com/owasp-amass/amass/v4/...@master"
    if ! generic_install_package "amass" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\t✨ Amass is already installed!"
fi
