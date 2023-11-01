__package__ = 'recono_sub'
import os
import requests
import json
from concurrent.futures import ThreadPoolExecutor
from common import common

from time import sleep
from random import uniform


class SubdomainRunner:
    def __init__(self, domains, output_dir, config):
        self.domains = domains
        self.domain_file = common.make_temp_file(domains)
        self.out_dir = f'{os.path.abspath(output_dir)}/'
        self.config = config
        self.binary_paths = config['binary_paths']
        self.api_keys = config['api_keys']

        self.threads = 10
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.wordlist_path = os.path.join(script_dir, '../wordlists', 'subdomain_master.txt')
        self.output_prefix = self.domain_file.split('/')[-1].split('_')[-2]
        os.makedirs(self.out_dir, exist_ok=True)

    def amass(self):
        out_path = os.path.join(self.out_dir, f'amass_{self.output_prefix}.json')
        amass_binary = self.binary_paths['amass']
        cmd = f'{amass_binary} enum -df {self.domain_file} -json {out_path}'
        print(f'Running Amass against {self.domains}\nOutputting results to {out_path}')
        stdout, stderr = common.run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def assetfinder(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_assetfinder, self.domains)

    def run_assetfinder(self, domain):
        out_path = os.path.join(self.out_dir, f'assetfinder_{domain}.txt')
        assetfinder_binary = self.binary_paths['assetfinder']
        cmd = f'{assetfinder_binary} --subs-only {domain}'
        print(f'Running AssetFinder against {domain}\nOutputting results to {out_path}')
        stdout, stderr = common.run_pipeline(cmd, output_path=out_path)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def bbot(self):
        out_path = os.path.join(self.out_dir, f'bbot_{self.out_dir}')
        bbot_binary = self.binary_paths['bbot']
        cmd = f'{bbot_binary} -t {self.domain_file} -f subdomain-enum -o {out_path} --silent -t {self.threads}'
        print(f'Running BBot against {self.domains}\nOutputting results to {out_path}')
        stdout, stderr = common.run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def c99_subdomain_finder(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_c99_subdomain_finder, self.domains)

    def run_c99_subdomain_finder(self, domain):
        out_path = os.path.join(self.out_dir, f'c99_{domain}.txt')
        key = self.api_keys["C99"]
        print(key)
        url = f'https://api.c99.nl/subdomainfinder?key={key}&domain={domain}'
        print(url)
        print(f'Running C99 against {domain}\nOutputting results to {out_path}')
        for i in range(5):  # 5 retries
            try:
                response = requests.get(url).text
                subdomains = response.split('<br>')
                if 'API key does not exist' in response:
                    print(f'There is a problem with your API key.\n{response}')
                with open(out_path, 'w') as file:
                    for subdomain in subdomains:
                        if subdomain:
                            file.write(f"{subdomain}\n")
                return
            except Exception as e:
                print(f"Attempt {i + 1} failed: {e}")
                sleep(uniform(0.1, 3))
        print(f"C99 failed after 5 attempts.")

    def crt_sh(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_crt_sh, self.domains)

    def run_crt_sh(self, domain):
        out_path = os.path.join(self.out_dir, f'crt-sh_{domain}.json')
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        print(f'Running Crt.sh against {domain}\nOutputting results to {out_path}')
        for i in range(5):  # 5 retries
            try:
                data = requests.get(url).json()
                with open(out_path, 'w') as file:
                    json.dump(data, file, indent=4)
                return
            except Exception as e:
                print(f"Attempt {i + 1} failed: {e}")
                sleep(uniform(0.1, 3))
        print(f"crt.sh failed after 5 attempts.")



    def github_subdomains(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_github_subdomains, self.domains)

    def run_github_subdomains(self, domain):
        out_path = os.path.join(self.out_dir, f'github-subdomains_{domain}.txt')
        github_subdomains_binary = self.binary_paths['github-subdomains']
        key = self.api_keys["GitHub"]
        cmd = f'{github_subdomains_binary} -e -d {domain} -t {key} -o {out_path}'
        print(f'Running GitHub against {domain}\nOutputting results to {out_path}')
        stdout, stderr = common.run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def hakrawler(self):
        out_path = os.path.join(self.out_dir, f'hakrawler_{self.output_prefix}.txt')
        hakrawler_binary = self.binary_paths['hakrawler']
        url_list = common.domains_to_urls(self.domains)
        url_file = common.make_temp_file(url_list)
        cmd = f'cat {url_file} | {hakrawler_binary} -subs -u -d 5'
        print(f'Running Hakrawler against {self.domain_file}\nOutputting results to {out_path}\n{cmd}')
        stdout, stderr = common.run_pipeline(cmd, output_path=out_path)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def knockpy(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_knockpy, self.domains)

    def run_knockpy(self, domain):
        out_path = os.path.join(self.out_dir, f'knockpy_{domain}')
        knockpy_binary = self.binary_paths['knockpy']
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        cmd = f'python {knockpy_binary} {domain} --no-http-code 404 -o {out_path} -th {self.threads}'
        print(f'Running KnockPy against {domain}\nOutputting results to {out_path}')
        stdout, stderr = common.run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def shuffledns(self):
        common.update_resolver_list(self.config)

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_shuffledns, self.domains)

    def run_shuffledns(self, domain):
        out_path = os.path.join(self.out_dir, f'shuffledns_{self.output_prefix}')
        shuffledns_binary = self.binary_paths['shuffledns']
        wordlist_file = self.config['wordlists']['subdomain_wordlist']
        resolver_file = self.config['wordlists']['resolver_file']
        massdns_path = self.config['binary_paths']['massdns']
        cmd = f'{shuffledns_binary} -d {domain} -w {wordlist_file} -r {resolver_file} -json -o {out_path} -m {massdns_path}'
        print(f'Running ShuffleDNS against {domain}\nOutputting results to {out_path}')
        stdout, stderr = common.common.run(cmd)


    def shosubgo(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_shosubgo, self.domains)

    def run_shosubgo(self, domain):
        out_path = os.path.join(self.out_dir, f'shosubgo_{domain}.txt')
        shosubgo_binary = self.binary_paths['shosubgo']
        key = self.api_keys['Shodan']
        cmd = f'{shosubgo_binary} -d {domain} -s {key}'
        print(f'Running Shosubgo against {domain}\nOutputting results to {out_path}')
        stdout, stderr = common.run_pipeline(cmd, output_path=out_path)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def subdomainizer(self):
        out_path = os.path.join(self.out_dir, f'subdomainizer_{self.output_prefix}.txt')
        cloud_path = f'{self.out_dir}subdomainizer_{self.output_prefix}_cloudservices.txt'
        subdomainizer_binary = self.binary_paths['subdomainizer']
        github_key = self.api_keys["GitHub"]
        url_list = common.domains_to_urls(self.domains)
        temp_file = common.make_temp_file(url_list)
        cmd = f'python {subdomainizer_binary} -l {temp_file} -g -gt {github_key} -o {out_path} -cop {cloud_path}'
        print(f'Running SubDomainizer against {self.domains}\nOutputting results to {out_path}')
        stdout, stderr = common.run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def subfinder(self):
        out_path = os.path.join(self.out_dir, f'subfinder_{self.output_prefix}')
        subfinder_binary = self.binary_paths['subfinder']
        temp_file = common.make_temp_file(self.domains)
        cmd = f'{subfinder_binary} -dL {temp_file} -all -silent -oJ -o {out_path} -t {self.threads}'
        print(f'Running SubFinder against {self.domains}\nOutputting results to {out_path}')
        stdout, stderr = common.run(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def waybackurls(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_waybackurls, self.domains)

    def run_waybackurls(self, domain):
        out_path = os.path.join(self.out_dir, f'waybackurls_{domain}.txt')
        waybackurls_binary = self.binary_paths['waybackurls']
        cmd = f'echo {domain} | {waybackurls_binary}'
        print(f'Running Waybackurls against {domain}\nOutputting results to {out_path}')
        stdout, stderr = common.run_pipeline(cmd, output_path=out_path)
        # print(f'STDOUT: {stdout}\nSTDERR
