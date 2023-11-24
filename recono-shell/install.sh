#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/libraries"
INSTALLERS_DIR="$SCRIPT_DIR/installers"
CONFIG_DIR="$HOME/.config/recono-shell"
CONFIG_FILE="$CONFIG_DIR/config.txt"
SRC_WORDLIST_DIR="$SCRIPT_DIR/wordlists"
DST_WORDLIST_DIR="$CONFIG_DIR/wordlists"
LOG_DIR="$CONFIG_DIR/logs"


source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-shell.lib"
source "$LIB_SCRIPT_DIR/install.lib"

echo "📦 Beginning recono-shell installation..."
# Create Config Directory
mkdir -p "$DST_WORDLIST_DIR"
mkdir -p $LOG_DIR

# Add directories to $PATH
declare -a ADDITIONAL_PATHS=("$HOME/go/bin" "/usr/local/go/bin" "/usr/local/bin/")
add_directories_to_path "${ADDITIONAL_PATHS[@]}"

# Set all bash script permissions in the project to 755
set_shell_script_permissions "$SCRIPT_DIR"

# Install installation dependencies and needed tools
check_and_run_script "$INSTALLERS_DIR/install-all-dependencies.sh"

# Prompt for API keys
SHODAN_API_KEY=$(prompt_for_api_key "Shodan")
GITHUB_API_KEY=$(prompt_for_api_key "Github")
C99_API_KEY=$(prompt_for_api_key "C99")

# Assign Wordlist Files
TRUSTED_RESOLVER_FILE="$DST_WORDLIST_DIR/trusted-resolvers.txt"
UNTRUSTED_RESOLVER_FILE="$DST_WORDLIST_DIR/untrusted-resolvers.txt"
SUBDOMAIN_MASTER_LIST="$DST_WORDLIST_DIR/subdomain-master.txt"

# Generate resolver lists
get_trusted_dns_resolver_list "$SRC_WORDLIST_DIR/trusted-resolvers.txt"
get_untrusted_dns_resolver_list "$SRC_WORDLIST_DIR/untrusted-resolvers.txt"



# Move Worldist files to .config
echo "Copying List files to $DST_WORDLIST_DIR..."
for ITEM in "$SRC_WORDLIST_DIR"/*; do
    if file_exists "$ITEM"; then
        cp -v "$ITEM" "$DST_WORDLIST_DIR"
    fi
done

# Load config variables (api keys and paths) into the config file
{
    echo "SHODAN_API_KEY=$SHODAN_API_KEY"
    echo "GITHUB_API_KEY=$GITHUB_API_KEY"
    echo "C99_API_KEY=$C99_API_KEY"
    echo "TRUSTED_RESOLVER_FILE=$TRUSTED_RESOLVER_FILE"
    echo "UNTRUSTED_RESOLVER_FILE=$UNTRUSTED_RESOLVER_FILE"
    echo "SUBDOMAIN_MASTER_LIST=$SUBDOMAIN_MASTER_LIST"
    echo "LOG_DIR=$LOG_DIR"
} > "$CONFIG_FILE"

chmod 600  "$CONFIG_FILE"

# TODO copy all files in this directory and below, into .config
