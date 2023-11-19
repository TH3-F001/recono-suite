#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
INSTALLERS_DIR="$SCRIPT_DIR/installers"

source "$SCRIPT_DIR/common/basic-operations.lib"
source "$INSTALLERS/install.lib"

echo "📦 Beginning recono-suite installation..."

# Add directories to $PATH
declare -a ADDITIONAL_PATHS=("$HOME/go/bin" "/usr/local/go/bin" "/usr/local/bin/")
add_directories_to_path "${ADDITIONAL_PATHS[@]}"

# Set all bash script permissions in the project to 755
set_shell_script_permissions "$SCRIPT_DIR"

# Install installation dependencies and needed tools
check_and_run_script "$INSTALLERS_DIR/install-all-dependencies.sh"

