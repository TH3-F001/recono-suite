#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LIB_SCRIPT_DIR="$SCRIPT_DIR/libraries"
INSTALLERS_DIR="$SCRIPT_DIR/installers"
CONFIG_DIR="$HOME/.config/recono-shell"
CONFIG_FILE="$CONFIG_DIR/config.txt"
SRC_WORDLIST_DIR="$SCRIPT_DIR/wordlists"
DST_WORDLIST_DIR="$CONFIG_DIR/wordlists"
LOG_DIR="$CONFIG_DIR/logs"
LOCAL_BIN_DIR="$HOME"/.local/bin

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-shell.lib"
source "$LIB_SCRIPT_DIR/install.lib"

echo "📦 Beginning recono-shell installation..."
# Create Config Directory



# Add directories to $PATH
mkdir -p "$LOCAL_BIN_DIR"
declare -a ADDITIONAL_PATHS=("$HOME/go/bin" "/usr/local/go/bin" "/usr/local/bin/" "$LOCAL_BIN_DIR")
add_directories_to_path "${ADDITIONAL_PATHS[@]}"

# Install installation dependencies and needed tools
check_and_run_script "$INSTALLERS_DIR/install-all-dependencies.sh"

# Move Worldist files to .config
echo "Copying files to $CONFIG_DIR..."
cp -v -r "$SCRIPT_DIR" "$HOME/.config"
find "$CONFIG_DIR" -type f -name "*.sh" -exec chmod 755 {} \;

echo "Linking Recono-Tools..."
for SCRIPT in "$CONFIG_DIR/recono-tools"/*.sh; do
    if [ -f "$SCRIPT" ]; then
        FILENAME=$(basename -- "$SCRIPT")
        LINKNAME="${FILENAME%.sh}"  # Remove the .sh extension

        # Create a symbolic link in LOCAL_BIN_DIR
        echo -e "\t Linking $SCRIPT to $LOCAL_BIN_DIR/$LINKNAME"
        ln -s "$SCRIPT" "$LOCAL_BIN_DIR/$LINKNAME"
    fi
done

# Assign Wordlist Files
mkdir -p "$DST_WORDLIST_DIR"
TRUSTED_RESOLVER_FILE="$DST_WORDLIST_DIR/trusted-resolvers.txt"
UNTRUSTED_RESOLVER_FILE="$DST_WORDLIST_DIR/untrusted-resolvers.txt"
SUBDOMAIN_MASTER_LIST="$DST_WORDLIST_DIR/subdomain-master.txt"

# Generate resolver lists
get_trusted_dns_resolver_list "$TRUSTED_RESOLVER_FILE"
get_untrusted_dns_resolver_list "$UNTRUSTED_RESOLVER_FILE"

# Prompt for API keys
SHODAN_API_KEY=$(prompt_for_api_key "Shodan")
GITHUB_API_KEY=$(prompt_for_api_key "Github")
C99_API_KEY=$(prompt_for_api_key "C99")

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
mkdir -p "$LOG_DIR"



