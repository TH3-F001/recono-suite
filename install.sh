#!/bin/bash

if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    # Check if Python version starts with 'Python 2.'
    if [[ $PYTHON_VERSION == Python\ 2.* ]]; then
        # Check if 'python3' exists
        if command -v python3 &> /dev/null; then
            PYTHON_CMD="python3"
        else
            echo "Python 3 is not installed. Please install it and try again."
            exit 1
        fi
    else
        PYTHON_CMD="python"
    fi
# If 'python' doesn't exist, try 'python3'
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "Neither Python 2 nor Python 3 is installed. Please install Python 3 and try again."
    exit 1
fi


if ! command -v pipx &> /dev/null; then
    echo 'pipx not found. Installing...'
    pip install --user pipx
    pipx ensurepath
fi


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_FILE="$SCRIPT_DIR/install_dependencies.py"
echo 'Installing recono-suite...'
pipx install $SCRIPT_DIR --force

echo 'Running install_dependencies.py...'
$PYTHON_CMD $INSTALL_FILE
