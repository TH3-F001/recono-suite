#!/bin/bash
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "Pip is not installed. Please install it and try again."
    exit 1
fi


if ! command -v pipx &> /dev/null; then
    echo 'pipx not found. Installing...'
    pip install --user pipx
    pipx ensurepath
fi


PYTHON_CMD="$HOME/.local/pipx/venvs/recono-suite/bin/python"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_FILE="$SCRIPT_DIR/install_dependencies.py"
echo 'Installing recono-suite...'
pipx install $SCRIPT_DIR --force

echo 'Running install_dependencies.py...'
$PYTHON_CMD $INSTALL_FILE
