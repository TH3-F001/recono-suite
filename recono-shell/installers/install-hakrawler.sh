#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"

echo "Installing Hakrawler..."
if ! command_exists hakrawler; then
    INSTALL_COMMAND="go install -v github.com/hakluke/hakrawler@latest"
    if ! generic_install_package "hakrawler" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\tHakrawler is already installed!"
fi