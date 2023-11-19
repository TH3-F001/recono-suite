#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"

echo "Installing Amass..."
if ! command_exists amass; then
    INSTALL_COMMAND="go install -v github.com/owasp-amass/amass/v4/...@master"
    if ! generic_install_package "amass" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\tAmass is already installed!"
fi
