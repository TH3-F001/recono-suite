import os
import requests
from shodan import Shodan
import json

import common
from common import run, get_config


class ShellCommand:
    def __init__(self, domain, output_dir, config, asn):
        self.domain = domain
        self.out_dir = f'{os.path.abspath(output_dir)}/'
        self.asn = asn
        self.binary_paths = config['binary_paths']
        self.api_keys = config['api_keys']
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.wordlist_path = os.path.join(script_dir, 'wordlists', 'subdomain_master.txt')
        os.makedirs(os.path.dirname(self.out_dir), exist_ok=True)

    def bbot(self):
        out_path = os.path.join(self.out_dir, f'bbot_{self.domain}')
        bbot_binary = self.binary_paths['bbot']
        cmd = f'{bbot_binary} -t {self.domain} -f subdomain-enum -o {out_path} --silent'
        print(f'Running BBot against {self.domain}\nOutputting results to {out_path}')
        stdout, stderr = run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def amass(self):
        out_path = os.path.join(self.out_dir, f'amass_{self.domain}.json')
        amass_binary = self.binary_paths['amass']
        if self.asn is None:
            cmd = f'{amass_binary} enum -d {self.domain} -active -brute -alts -json {out_path}'
        else:
            cmd = f'{amass_binary} enum -d {self.domain} -asn {self.asn} -active -brute -alts -json {out_path}'

        print(f'Running Amass against {self.domain}\nOutputting results to {out_path}')
        stdout, stderr = run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')


    def gobuster(self):
        out_path = os.path.join(self.out_dir, f'gobuster_{self.domain}.txt')
        gobuster_binary = self.binary_paths['gobuster']
        cmd = f'{gobuster_binary} dns -d {self.domain} -w {self.wordlist_path} -o {out_path}'
        print(f'Running GoBuster against {self.domain}\nOutputting results to {out_path}')

        stdout, stderr = run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def subfinder(self):
        out_path = os.path.join(self.out_dir, f'subfinder_{self.domain}.json')
        subfinder_binary = self.binary_paths['subfinder']
        cmd = f'{subfinder_binary} -d {self.domain} -all -silent -oJ -o {out_path}'
        print(f'Running SubFinder against {self.domain}\nOutputting results to {out_path}')

        stdout, stderr = run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def subscraper(self):
        out_path = os.path.join(self.out_dir, f'subscraper_{self.domain}.txt')
        subscraper_binary = self.binary_paths['subscraper']
        bevigil_key = self.api_keys["BeVigil"]
        cmd = f'{subscraper_binary} --all {self.domain} -r {out_path} --bevigil_key {bevigil_key}'
        print(f'Running SubScraper against {self.domain}\nOutputting results to {out_path}')

        stdout, stderr = run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def subdomainizer(self):
        out_path = os.path.join(self.out_dir, f'subdomainizer_{self.domain}.txt')
        cloud_path = f'{self.out_dir}subdomainizer_{self.domain}_cloudservices.txt'
        subdomainizer_binary = self.binary_paths['subdomainizer']
        github_key = self.api_keys["GitHub"]
        cmd = f'python {subdomainizer_binary} -u http://{self.domain} -d {self.domain} -g -gt {github_key} -o {out_path} -cop {cloud_path}'
        print(f'Running SubDomainizer against {self.domain}\nOutputting results to {out_path}')
        stdout, stderr = run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def knockpy(self):
        out_path = os.path.join(self.out_dir, f'knockpy_{self.domain}')
        knockpy_binary = self.binary_paths['knockpy']
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        cmd = f'{knockpy_binary} {self.domain} --no-http-code 404 -o {out_path}'
        print(f'Running KnockPy against {self.domain}\nOutputting results to {out_path}')

        stdout, stderr = run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def assetfinder(self):
        out_path = os.path.join(self.out_dir, f'assetfinder_{self.domain}.txt')
        assetfinder_binary = self.binary_paths['assetfinder']
        cmd = f'{assetfinder_binary} --subs-only {self.domain} > {out_path}'
        print(f'Running AssetFinder against {self.domain}\nOutputting results to {out_path}')

        stdout, stderr = run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def shodan(self):
        out_path = os.path.join(self.out_dir, f'shodan_{self.domain}.txt')
        key = self.api_keys['Shodan']
        shodan = Shodan(key)
        hostnames = set()
        try:
            print(f'Running Shodan against {self.domain}\nOutputting results to {out_path}')
            results = shodan.search(f'hostname:{self.domain}', fields='hostnames')

            for result in results['matches']:
                hostnames.update(result['hostnames'])
            with open(out_path, 'w') as file:
                for hostname in hostnames:
                    print(hostname)
                    file.write(f'{hostname}\n')

        except shodan.APIError as e:
            print(f'Error in Shodan:\n{e}')

    def github_subdomains(self):
        out_path = os.path.join(self.out_dir, f'github-subdomains_{self.domain}.txt')
        github_subdomains_binary = self.binary_paths['github-subdomains']
        key = self.api_keys["GitHub"]
        cmd = f'{github_subdomains_binary} -d {self.domain} -t {key} -o {out_path}'
        print(f'Running GitHub against {self.domain}\nOutputting results to {out_path}')
        stdout, stderr = run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    # TODO Set up waybackurls. (Will need to strip directories from the found subdomains) Also good for directories
    def waybackurls(self):
        out_path = os.path.join(self.out_dir, f'waybackurls_{self.domain}.txt')
        waybackurls_binary = self.binary_paths['waybackurls']
        cmd = f'echo {self.domain} | {waybackurls_binary} > {out_path}'
        print(f'Running Waybackurls against {self.domain}\nOutputting results to {out_path}')
        stdout, stderr = run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    # ToDo Will need to strip directories and unique found subdomains Also good for directories
    def hakrawler(self):
        out_path = os.path.join(self.out_dir, f'hakrawler_{self.domain}.json')
        hakrawler_binary = self.binary_paths['hakrawler']
        cmd = f'echo http://{self.domain} | {hakrawler_binary} -subs -u -json > {out_path}'
        print(f'Running Hakrawler against {self.domain}\nOutputting results to {out_path}')
        stdout, stderr = run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    # Will just replace my shodan API calls.
    def shosubgo(self):
        out_path = os.path.join(self.out_dir, f'shosubgo_{self.domain}.txt')
        shosubgo_binary = self.binary_paths['shosubgo']
        key = self.api_keys['Shodan']
        cmd = f'{shosubgo_binary} -d {self.domain} -s {key} > {out_path}'
        stdout, stderr = run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')


    def c99_subdomain_finder(self):
        out_path = os.path.join(self.out_dir, f'c99_{self.domain}.txt')
        key =self.api_keys["C99"]
        url = f'https://api.c99.nl/subdomainfinder?key={key}&domain={self.domain}'
        print(f'Running C99 against {self.domain}\nOutputting results to {out_path}')

        response = requests.get(url).text
        subdomains = response.split('<br>')
        with open(out_path, 'w') as file:
            for subdomain in subdomains:
                if subdomain:
                    file.write(f"{subdomain}\n")


    def crt_sh(self):
        out_path = os.path.join(self.out_dir, f'crt-sh_{self.domain}.json')
        url = f"https://crt.sh/?q=%.{self.domain}&output=json"
        print(f'Running Crt.sh against {self.domain}\nOutputting results to {out_path}')

        data = requests.get(url).json()
        with open(out_path, 'w') as file:
            json.dump(data, file, indent=4)

