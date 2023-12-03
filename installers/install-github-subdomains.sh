#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"
echo -e "\n📦 Installing GitHub-Subdomains..."
if ! command_exists github-subdomains; then
    INSTALL_COMMAND="go install github.com/gwen001/github-subdomains@latest"
    if ! generic_install_package "github-subdomains" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\t✨ GitHub-Subdomains is already installed!"
fi