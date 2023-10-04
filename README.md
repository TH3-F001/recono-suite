# recono-suite

## Description
Just a shitty little collection of scripts for enumerating seed domains, subdomains, and directories for bug bounty
All they do for the most part is multi-processed, and multi-threaded execution of common recon shell commands, send the output to a
common directory, and then parses the results to a master file, which is then iterated over again until no new results are
found

### Tools Used:

#### Subdomain Enumeration:
- Amass
- Bbot
- C99
- crt.sh
- GoBuster
- Github-Subdomains
- Hakrawler
- Knockpy
- ShoSubGo
- Subfinder
- Subscraper
- Subdomainizer
- Waybackurls

## Disclaimer:
At this time the project and the install process have only been tested on Fedora 27. I do plan to do more testing in the future.

## Install:

### 1) Clone the repository and enter the directory:
    git clone git@github.com:TH3-F001/recono-suite.git
    cd recono-suite

### 2) Give install.sh executable privileges:
    chmod +x install.sh

### 3) Run install.sh (requires python 3.10 or higher):
    ./install.sh

### 4) Provide your API keys when prompted.
You'll be prompted for the following API Keys:
- GitHub
- Bevigil
- C99
- Shodan
- Censys

### 5) Provide sudo credentials to install dependencies:
The following shell tools are required to run this tool:
- amass
- assetfinder
- bbot
- gobuster
- github-subdomains
- knockpy
- shodan
- subfinder
- subscraper
- subdomainizer
