#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"

echo "Installing GitHub-Subdomains..."
if ! command_exists github-subdomains; then
    INSTALL_COMMAND="go install github.com/gwen001/github-subdomains@latest"
    if ! generic_install_package "github-subdomains" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\tGitHub-Subdomains is already installed!"
fi