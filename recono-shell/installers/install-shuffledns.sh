#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"

# MassDNS is required in order to run ShuffleDNS
echo -e "\n📦 Installing MassDNS..."
if ! command_exists massdns; then
    TEMP_DIR="/tmp/massdns"
        if ! directory_exists $TEMP_DIR; then
            mkdir $TEMP_DIR
        fi

    git clone https://github.com/guelfoweb/knock.git "$TEMP_DIR"
    cd "$TEMP_DIR" || exit
    make
    sudo make install
else
    echo -e "\t✨ MassDNS is already installed!"
fi

if ! command_exists massdns; then
    exit 1
fi


echo -e "\n📦 Installing ShuffleDNS..."

if ! command_exists shuffledns; then
    INSTALL_COMMAND="go install github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest"
    if ! generic_install_package "shuffledns" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\t✨ ShuffleDNS is already installed!"
fi