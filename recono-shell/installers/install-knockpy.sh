#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"

echo -e "\n📦 Installing Knockpy..."
if ! command_exists knockpy; then
    TEMP_DIR="/tmp/knockpy"
    if ! directory_exists $TEMP_DIR; then
        mkdir $TEMP_DIR
    fi

    git clone https://github.com/guelfoweb/knock.git "$TEMP_DIR"
    cd "$TEMP_DIR" || exit
    INSTALL_COMMAND="sudo python3 setup.py install"
    
    if ! generic_install_package "knockpy" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\t✨ Knockpy is already installed!"
fi