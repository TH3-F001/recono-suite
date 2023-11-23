#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"
CONFIG_DIR="$HOME/.config/recono-shell"
source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"

echo -e "\n📦 Installing Bbot..."
if ! command_exists bbot; then
    INSTALL_COMMAND="pipx install bbot --force"
    if ! generic_install_package "bbot" "$INSTALL_COMMAND"; then
        exit 1
    fi
else
    echo -e "\t✨ Bbot is already installed!"
fi

# Create bbot user with sudo access to the bbot binary with no password (and nothing else)

BBOT_PATH=$(which bbot)
CURRENT_USER=$(whoami)
echo "$CURRENT_USER ALL=(ALL) NOPASSWD: $BBOT_PATH" | sudo tee /etc/sudoers.d/bbot-nopasswd
sudo chmod 440 /etc/sudoers.d/bbot-nopasswd


# sudo -u ubbot bbot --install-all-deps
