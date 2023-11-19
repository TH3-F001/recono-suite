#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

source "$SCRIPT_DIR/../common/basic-operations.lib"
source "$SCRIPT_DIR/install.lib"

echo "Installing Knockpy..."
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
    echo -e "\tKnockpy is already installed!"
fi