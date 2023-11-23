#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"

# MassDNS is required in order to run ShuffleDNS
echo "📦 Installing MassDNS..."
if ! command_exists massdns; then
    TEMP_DIR="/tmp/massdns"
        if ! directory_exists "$TEMP_DIR"; then
            mkdir "$TEMP_DIR"
        else
            rm -rf "$TEMP_DIR"
        fi

    git clone https://github.com/blechschmidt/massdns.git "$TEMP_DIR"
    cd "$TEMP_DIR" || exit
    make 
    sudo make install
else
    echo -e "\tMassDNS is already installed!"
fi

if ! command_exists massdns; then
    exit 1
fi


if ! command_exists shuffledns; then
    INSTALL_COMMAND="go install github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest"
    if ! generic_install_package "shuffledns" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\tShuffleDNS is already installed!"
fi