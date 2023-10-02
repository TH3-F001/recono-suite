# recono-suite

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
