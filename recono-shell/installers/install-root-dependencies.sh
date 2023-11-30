#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/../libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/install.lib"

declare -a REQUIRED_DEPENDENCIES=("pip3" "pipx" "go" "git" "make" "curl" "wget" "expect" "sqlite" "jq" )
declare -a ABSENT_DEPENDENCIES

check_and_add_dependency() {
    local DEP=$1

    if ! check_argument $DEP; then
        print_error "check_argument expects a dependency as an argument"
    fi

    if ! command_exists "$DEP"; then
        ABSENT_DEPENDENCIES+=("$DEP")
    fi
}


python_requirements_are_met() {
    if ! command_exists python3 &> /dev/null; then
        print_error "Python is not installed."
        return 1
    fi

    PYTHON_VERSION=$(python3 -V | cut -d ' ' -f 2)
    if [[ "$(printf '%s\n' "3.10" "$PYTHON_VERSION" | sort -V | head -n1)" == "3.10" ]]; then
        echo -e "\t ✨ Python version is 3.10 or higher. Continuing..."
        return 0
    else
        echo -e "\t Python version is lower than 3.10. Adding to install list..."
        return 1
    fi
}


# Check if base packages needed for the rest of the installation process are installed
if ! python_requirements_are_met; then 
    ABSENT_DEPENDENCIES+=("python3")
fi

for DEP in "${REQUIRED_DEPENDENCIES[@]}"; do
    check_and_add_dependency "$DEP"
done

# Install Absent Dependencies based on package manager
if [ ${#ABSENT_DEPENDENCIES[@]} -ne 0 ]; then
    if command_exists apt &> /dev/null; then
        install_with_apt "${ABSENT_DEPENDENCIES[@]}"
    elif command_exists dnf &> /dev/null; then
        install_with_yum "${ABSENT_DEPENDENCIES[@]}"
    elif command_exists yum &> /dev/null; then
        install_with_dnf "${ABSENT_DEPENDENCIES[@]}"
    elif command_exists pacman &> /dev/null; then
        install_with_pacman "${ABSENT_DEPENDENCIES[@]}"
    elif command_exists zypper &> /dev/null; then
        install_with_zypper "${ABSENT_DEPENDENCIES[@]}"
    elif command_exists emerge &> /dev/null; then
        install_with_emerge "${ABSENT_DEPENDENCIES[@]}"
    else
        print_error "No Known Package Manager Found"
        echo "Please install the following packages manually:"
        for ITEM in "${ABSENT_DEPENDENCIES[@]}"; do
            echo -e "\t$ITEM"
        done
        exit 1
    fi
fi

# Install pipx with python if still absent
if ! command_exists pipx &> /dev/null; then
    if $PIPX_ABSENT; then
        python3 -m pip install --user pipx
        python3 -m pipx ensurepath
    fi
fi

# Make a final check to ensure all dependencies are installed
SUCCESS=0

for DEP in "${REQUIRED_DEPENDENCIES[@]}"; do
    if ! command_exists "$DEP"; then
        SUCCESS=1
        break
    fi
done

# Add directories to $PATH


PROFILE_FILE="$HOME/.profile"
PATH_ADDITION=""

for DIR in "${ADDITIONAL_PATHS[@]}"; do
    if ! is_in_path "$DIR" ; then
        PATH_ADDITION="$DIR:$PATH_ADDITION"
    fi
done

if [ -n "$PATH_ADDITION" ]; then
    export PATH="$PATH_ADDITION$PATH"
    EXPORT_LINE="export PATH=\"$PATH_ADDITION\$PATH\""
    if ! grep -qF "$PATH_ADDITION" "$PROFILE_FILE"; then
        echo "$EXPORT_LINE" >> "$PROFILE_FILE"
    fi
fi


exit $SUCCESS