import subprocess
import os
import requests
from bbot.scanner import Scanner
from bs4 import BeautifulSoup
import time
import re
from common import get_api_keys
import json

class ShellCommand:
    def __init__(self, domain, output_dir, config_file=None):
        self.domain = domain
        self.out_dir = f'{output_dir}/'
        self.asn = self.get_asn()
        self.api_keys = get_api_keys(config_file=config_file)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.wordlist_path = os.path.join(script_dir, 'wordlists', 'subdomain_master.txt')
        os.makedirs(os.path.dirname(self.out_dir), exist_ok=True)

    def _run(self, cmd):
        command = cmd.split(' ')
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')

    def get_asn(self):
        url = f'https://www.robtex.com/dns-lookup/{self.domain}#records'
        response = requests.get(url).content
        soup = BeautifulSoup(response, 'html.parser')

        asn_link = soup.find('a', string=re.compile(r'AS\d{1,10}'))
        if asn_link:
            asn = asn_link.text.strip('AS')
            asname = soup.find('td', string='asname').find_next('td').text
            print(f'ASN:\t{asn}\nName:\t{asname}')
            use_asn = input(f'Would you like to add this ASN to your scanning parameters? Y/N: ').strip().lower()
            if use_asn == 'y':
                print(f'Adding ASN {asn} to scanning parameters.')
            else:
                print('Running scan without ASN parameter')
                asn = None
        else:
            print('ASN not found')
            asn = None
        return asn

    def bbot(self):
        out_path = f'{self.out_dir}'
        cmd = f'bbot -t {self.domain} -f subdomain-enum -o {out_path}/bbot_{self.domain} --silent'
        self._run(cmd)

    def amass(self):
        out_path = f'{self.out_dir}/amass_{self.domain}.json'
        if self.asn == None:
            cmd = f'amass enum -d {self.domain} -active -brute -alts -json {out_path}'
        else:
            cmd = f'amass enum -d {self.domain} -asn {self.asn} -active -brute -alts -json {out_path}'
        self._run(cmd)

    def gobuster(self):
        out_path = f'{self.out_dir}/gobuster_{self.domain}.txt'
        cmd = f'gobuster dns -d {self.domain} -w {self.wordlist_path} -o {out_path}'
        self._run(cmd)

    def subfinder(self):
        out_path = f'{self.out_dir}/subfinder_{self.domain}.json'
        cmd = f'subfinder -d {self.domain} -all -silent -oJ -o {out_path}'
        self._run(cmd)

    def subscraper(self):
        out_path = f'{self.out_dir}/subscraper_{self.domain}.txt'
        cmd = f'subscraper --all {self.domain} -r {out_path} --bevigil_key {self.api_keys["BeVigil"]}'
        self._run(cmd)

    def subdomainizer(self):
        out_path = f'{self.out_dir}/subdomainizer_{self.domain}.txt'
        cloud_path = f'{self.out_dir}/subdomainizer_{self.domain}_cloudservices.txt'
        cmd = f'subdomainizer -u http://{self.domain} -d {self.domain} -g -gt {self.api_keys["GitHub"]} -o {out_path} -cop {cloud_path}'
        self._run(cmd)

    def knockpy(self):
        out_path = f'{self.out_dir}/knockpy'
        cmd = f'knockpy {self.domain} --no-http-code 404 -o {out_path}'
        self._run(cmd)

    def assetfinder(self):
        out_path = f'{self.out_dir}/assetfinder_{self.domain}.txt'
        cmd = f'assetfinder --subs-only {self.domain} > {out_path}'
        self._run(cmd)


    def shodan(self): #outputs as a semicolon delimited list
        out_path = f'{self.out_dir}/shodan_{self.domain}.txt'
        cmd = f'shodan search --fields hostnames "hostname:{self.domain}" > {out_path}'
        self._run(cmd)

    def github_subdomains(self):
        out_path = f'{self.out_dir}/github-subdomains_{self.domain}.txt'
        cmd = f'github-subdomains -d {self.domain} -t {self.api_keys["GitHub"]} -o {self.out_dir}'
        self._run(cmd)

    def c99_subdomain_finder(self):
        out_path = f'{self.out_dir}/c99_{self.domain}.txt'
        url = f'https://api.c99.nl/subdomainfinder?key={self.api_keys["C99"]}&domain={self.domain}'
        response = requests.get(url).text
        subdomains = response.split('<br>')
        with open(out_path, 'w') as file:
            for subdomain in subdomains:
                if subdomain:
                    file.write(f"{subdomain}\n")

    def crt_sh(self):
        out_path = f'{self.out_dir}/crt-sh_{self.domain}.json'
        url = f"https://crt.sh/?q=%.{self.domain}&output=json"
        data = requests.get(url).json()
        with open(out_path, 'w') as file:
            json.dump(data, file, indent=4)

