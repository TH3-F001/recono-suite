# recono-suite

## Description
Just a humble, dead simple collection of scripts for assisting in the information gathering stages of pentesting

## Install:
'''
git clone https://github.com/TH3-F001/recono-suite.git
cd recono-suite
chmod +x install.sh
./install.sh
'''

## Uninstall:
```
cd $HOME/.config/recono-suite
./uninstall.sh
```

## Requirements:

### Api Keys:
- C99
- Shodan
- Github

### GoLang Version
go version go1.21.4 or higher

## Tools Used:

### Subdomain Enumeration:
- Amass
- Bbot
- C99
- crt.sh
- ShuffleDNS
- Github-Subdomains
- Hakrawler
- Knockpy
- ShoSubGo
- Subfinder
- Subdomainizer
- Waybackurls


## Disclaimers:

### Installation Process Disclaimer
At this time the project and the install process have only been tested on Garuda Linux but was written with all linux distros in mind. If subfinder doesnt install manually install the latest go version.
I do plan to do more testing in the future.

### Recono-Sub Limitations:
This script utilizes a huge shuffledns wordlist, and as such can take up a lot of time and bandwitdth. It is best used with small domain chunks, which can be changed in the script.
I am always considering ways to speed this up, and make it more feasible to run recursively.

### A Note On API Keys:
bbot, amass, and subfinder all have config files in which you can place many different api keys which can help find more hits. 
Asking the user for these keys, and automatically populating the config files is out of scope of this tool as I want it to be accessible and quick to roll up (say on a collection of cloud machines).
Even so I strongly recommend that if you use any of these tools you take the time to fill out the API configurations on each one for maximum coverage. 




