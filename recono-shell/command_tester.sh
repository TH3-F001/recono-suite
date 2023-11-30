#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
RUNNER_DIR="$SCRIPT_DIR/subdomain-runners"
LIB_SCRIPT_DIR="$SCRIPT_DIR/libraries"

source "$LIB_SCRIPT_DIR/basic-operations.lib"
source "$LIB_SCRIPT_DIR/recono-shell.lib"

DOMAINS="chinesehappiness.com,eastwindcomputers.com,lacity.gov"
OUTPUT_ROOT="$HOME/Downloads/recono-testing/results"

# Amass
AMASS_OUT_DIR="$OUTPUT_ROOT/amass"
AMASS_SCRIPT="$RUNNER_DIR/run-amass.sh"
mkdir -p "$AMASS_OUT_DIR"
$AMASS_SCRIPT -d "$DOMAINS" -o "$AMASS_OUT_DIR"

# Assetfinder
ASSETFINDER_OUT_DIR="$OUTPUT_ROOT/assetfinder"
ASSETFINDER_SCRIPT="$RUNNER_DIR/run-assetfinder.sh"
mkdir -p "$ASSETFINDER_OUT_DIR"
$ASSETFINDER_SCRIPT -d "$DOMAINS" -o "$ASSETFINDER_OUT_DIR"

# Bbot
BBOT_OUT_DIR="$OUTPUT_ROOT/bbot"
BBOT_SCRIPT="$RUNNER_DIR/run-bbot.sh"
mkdir -p "$BBOT_OUT_DIR"
$BBOT_SCRIPT -d "$DOMAINS" -o "$BBOT_OUT_DIR"

# Github Subdomains
GITHUB_SUBDOMAINS_OUT_DIR="$OUTPUT_ROOT/github-subdomains"
GITHUB_SUBDOMAINS_SCRIPT="$RUNNER_DIR/run-github-subdomains.sh"
mkdir -p "$GITHUB_SUBDOMAINS_OUT_DIR"
$GITHUB_SUBDOMAINS_SCRIPT -d "$DOMAINS" -o "$GITHUB_SUBDOMAINS_OUT_DIR"

# Hakrawler
HAKRAWLER_OUT_DIR="$OUTPUT_ROOT/hakrawler"
HAKRAWLER_SCRIPT="$RUNNER_DIR/run-hakrawler.sh"
mkdir -p "$HAKRAWLER_OUT_DIR"
$HAKRAWLER_SCRIPT -d "$DOMAINS" -o "$HAKRAWLER_OUT_DIR"

# Shosubgo
SHOSUBGO_OUT_DIR="$OUTPUT_ROOT/shosubgo"
SHOSUBGO_SCRIPT="$RUNNER_DIR/run-shosubgo"
mkdir -p "$SHOSUBGO_OUT_DIR"
$SHOSUBGO_SCRIPT -d "$DOMAINS" -o "$SHOSUBGO_OUT_DIR"

# # Shuffledns
# SHUFFLEDNS_OUT_DIR="$OUTPUT_ROOT/shuffledns"
# SHUFFLEDNS_SCRIPT="$RUNNER_DIR/run-shuffledns.sh"
# mkdir -p "$SHUFFLEDNS_OUT_DIR"
# $SHUFFLEDNS_SCRIPT -d "$DOMAINS" -o "$SHUFFLEDNS_OUT_DIR"

# Subdomainizer
SUBDOMAINIZER_OUT_DIR="$OUTPUT_ROOT/subdomainizer"
SUBDOMAINIZER_SCRIPT="$RUNNER_DIR/run-subdomainizer.sh"
mkdir -p "$SUBDOMAINIZER_OUT_DIR"
$SUBDOMAINIZER_SCRIPT -d "$DOMAINS" -o "$SUBDOMAINIZER_OUT_DIR"

# Subfinder
SUBFINDER_OUT_DIR="$OUTPUT_ROOT/subfinder"
SUBFINDER_SCRIPT="$RUNNER_DIR/run-subfinder.sh"
mkdir -p "$SUBFINDER_OUT_DIR"
$SUBFINDER_SCRIPT -d "$DOMAINS" -o "$SUBFINDER_OUT_DIR"

# Waybackurls
WAYBACKURLS_OUT_DIR="$OUTPUT_ROOT/waybackurls"
WAYBACKURLS_SCRIPT="$RUNNER_DIR/run-waybackurls.sh"
mkdir -p "$WAYBACKURLS_OUT_DIR"
$WAYBACKURLS_SCRIPT -d "$DOMAINS" -o "$WAYBACKURLS_OUT_DIR"
