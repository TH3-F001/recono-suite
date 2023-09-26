import os
import requests
from shodan import Shodan
import json

from common import run


class ShellCommand:
    def __init__(self, domain, output_dir, api_keys, asn):
        self.domain = domain
        self.out_dir = f'{os.path.abspath(output_dir)}/'
        self.asn = asn
        self.api_keys = api_keys
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.wordlist_path = os.path.join(script_dir, 'wordlists', 'subdomain_master.txt')
        os.makedirs(os.path.dirname(self.out_dir), exist_ok=True)

    def bbot(self):
        out_path = os.path.join(self.out_dir, f'bbot_{self.domain}')
        cmd = f'bbot -t {self.domain} -f subdomain-enum -o {out_path}bbot_{self.domain} --silent'
        print(f'Running BBot against {self.domain}\nOutputting results to {out_path}')
        stdout, stderr = run(cmd)
        print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def amass(self):
        out_path = os.path.join(self.out_dir, f'amass_{self.domain}.json')
        if self.asn == None:
            cmd = f'amass enum -d {self.domain} -active -brute -alts -json {out_path}'
        else:
            cmd = f'amass enum -d {self.domain} -asn {self.asn} -active -brute -alts -json {out_path}'

        print(f'Running Amass against {self.domain}\nOutputting results to {out_path}')
        stdout, stderr = run(cmd)
        print(f'STDOUT: {stdout}\nSTDERR: {stderr}')


    def gobuster(self):
        out_path = os.path.join(self.out_dir, f'gobuster_{self.domain}.txt')
        cmd = f'gobuster dns -d {self.domain} -w {self.wordlist_path} -o {out_path}'
        print(f'Running GoBuster against {self.domain}\nOutputting results to {out_path}')

        stdout, stderr = run(cmd)
        print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def subfinder(self):
        out_path = os.path.join(self.out_dir, f'subfinder_{self.domain}.json')
        cmd = f'subfinder -d {self.domain} -all -silent -oJ -o {out_path}'
        print(f'Running SubFinder against {self.domain}\nOutputting results to {out_path}')

        stdout, stderr = run(cmd)
        print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def subscraper(self):
        out_path = os.path.join(self.out_dir, f'subscraper_{self.domain}.txt')
        bevigil_key = self.api_keys["BeVigil"]
        cmd = f'subscraper --all {self.domain} -r {out_path} --bevigil_key {bevigil_key}'
        print(f'Running SubScraper against {self.domain}\nOutputting results to {out_path}')

        stdout, stderr = run(cmd)
        print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def subdomainizer(self):
        out_path = os.path.join(self.out_dir, f'subdomainizer_{self.domain}.txt')
        cloud_path = f'{self.out_dir}subdomainizer_{self.domain}_cloudservices.txt'
        subdomainizer = os.path.expanduser('~/bin/SubDomainizer/SubDomainizer.py')
        github_key = self.api_keys["GitHub"]
        cmd = f'python {subdomainizer} -u http://{self.domain} -d {self.domain} -g -gt {github_key} -o {out_path} -cop {cloud_path}'
        print(f'Running SubDomainizer against {self.domain}\nOutputting results to {out_path}')
        stdout, stderr = run(cmd)
        print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def knockpy(self):
        out_path = os.path.join(self.out_dir, f'knockpy_{self.domain}')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        cmd = f'knockpy {self.domain} --no-http-code 404 -o {out_path}'
        print(f'Running KnockPy against {self.domain}\nOutputting results to {out_path}')

        stdout, stderr = run(cmd)
        print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def assetfinder(self):
        out_path = os.path.join(self.out_dir, f'assetfinder_{self.domain}.txt')
        cmd = f'assetfinder --subs-only {self.domain} > {out_path}'
        print(f'Running AssetFinder against {self.domain}\nOutputting results to {out_path}')

        stdout, stderr = run(cmd)
        print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

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
        key = self.api_keys["GitHub"]
        github_subdomains = os.path.expanduser('~/go/bin/github-subdomains')
        cmd = f'{github_subdomains} -d {self.domain} -t {key} -o {out_path}'
        print(f'Running GitHub against {self.domain}\nOutputting results to {out_path}')
        print(cmd)
        stdout, stderr = run(cmd)
        print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

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

