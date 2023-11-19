__package__ = 'recono_sub'
import os
import time

import requests
import json
from concurrent.futures import ThreadPoolExecutor
from common import common

from time import sleep
from random import uniform


class SubdomainRunner:
    def __init__(self, output_dir, config, debug=False):
        self.out_dir = f'{os.path.abspath(output_dir)}/'
        self.config = config
        self.api_keys = config['api_keys']

        self.threads = 10
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.wordlist_path = os.path.join(script_dir, '../wordlists', 'subdomain_master.txt')
        os.makedirs(self.out_dir, exist_ok=True)
        self.debug = debug

    def run_tool(self, tool_name, domains, mode='passive'):
        start_time = time.time()
        if mode not in ['active', 'passive']:
            raise ValueError('Invalid mode. Mode must be either "active" or "passive')
        print(f'Running {tool_name.capitalize()} against {", ".join(domains)}...')
        tool_config = self.config['tools'][tool_name]

        out_ext = tool_config.get('output_extension', '')
        out_ext = f'.{out_ext}' if out_ext else ''

        domain_arg_type = tool_config.get('domain_arg_type', '')
        cmd_arg_info = tool_config.get('run_command_args', {})

        shell_arg = bool(cmd_arg_info.get('shell', False))
        env_arg = os.environ if cmd_arg_info.get('env', '') == 'os.environ' else None
        cmd_requires_outpath = cmd_arg_info.get('output_path', False)

        if domain_arg_type in ['comma_separated', 'domain_file']:
            domain_input = ','.join(domains) if domain_arg_type == 'comma_separated' else common.make_temp_file(domains)
            domains_hash = common.hash_object(domains)
            out_path = os.path.join(self.out_dir, f'{tool_name}_{domains_hash}{out_ext}')
            supplemental_out_path = out_path if cmd_requires_outpath else None
            cmd = self.build_command(tool_name, domain_input, out_path, mode)
            result = common.run_command(cmd, shell=shell_arg, env=env_arg, output_path=supplemental_out_path, debug=True)
        else:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                for domain in domains:
                    out_path = os.path.join(self.out_dir, f'{tool_name}_{domain}{out_ext}')
                    supplemental_out_path = out_path if cmd_requires_outpath else None
                    cmd = self.build_command(tool_name, domain, out_path, mode)
                    executor.submit(common.run_command(cmd, shell=shell_arg, env=env_arg, output_path=supplemental_out_path, debug=True))

    def build_command(self, tool_name, domain_input, out_path, mode):
        tool_config = self.config['tools'][tool_name]

        command_template = tool_config.get(f'{mode}_cmd', '')

        placeholders = {
            '<BINARY>': tool_config['binary_path'],
            '<DOMAIN_ARG>': domain_input,
            '<RESOLVER_FILE>': self.config['wordlists']['resolver_file'],
            '<OUT_PATH>': out_path,
            '<GITHUB_KEY>': self.api_keys['GitHub'],
            '<URL_LIST_FILE>': common.generate_url_file_from_domains(domain_input),
            '<THREADS>': str(self.threads),
            '<SHODAN_KEY>': self.api_keys['Shodan'],
            '<WORDLIST_FILE>': self.config['wordlists']['subdomain_wordlist'],
            '<MASSDNS_PATH>': self.config['tools']['massdns']['binary_path'],
            '<CLOUD_PATH>': f'{out_path}_cloudservices.txt'
        }

        for placeholder, value in placeholders.items():
            command_template = command_template.replace(placeholder, value)

        return command_template

    def make_api_call(url, out_path, response_type='text', max_retries=5, sleep_range=(0.1, 3)):
        for i in range(max_retries):
            try:
                response = requests.get(url)
                if response_type == 'json':
                    data = response.json()
                    with open(out_path, 'w') as file:
                        json.dump(data, file, indent=4)
                else:
                    data = response.text
                    with open(out_path, 'w') as file:
                        for line in data.split('<br>'):
                            if line:
                                file.write(f"{line}\n")
                return
            except Exception as e:
                print(f"Attempt {i + 1} failed: {e}")
                sleep(uniform(*sleep_range))
        print(f"API call failed after {max_retries} attempts.")

    def amass(self, domains, mode='passive'):
        self.run_tool('amass', domains, mode=mode)

    def assetfinder(self, domains):
        self.run_tool('assetfinder', domains, mode='passive')

    def bbot(self, domains, mode='passive'):
        self.run_tool('bbot', domains, mode=mode)

    def c99_subdomain_finder(self, domains):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_c99_subdomain_finder, domains)

    def run_c99_subdomain_finder(self, domain):
        out_path = os.path.join(self.out_dir, f'c99_{domain}.txt')
        key = self.api_keys["C99"]
        url = f'https://api.c99.nl/subdomainfinder?key={key}&domain={domain}'
        print(url)
        print(f'Running C99 against {domain}\n\tOutputting results to {out_path}')
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

    def crt_sh(self, domains):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_crt_sh, domains)

    def run_crt_sh(self, domain):
        out_path = os.path.join(self.out_dir, f'crt-sh_{domain}.json')
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        print(f'Running Crt.sh against {domain}\n\tOutputting results to {out_path}')
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

    def github_subdomains(self, domains):
        self.run_tool('github-subdomains', domains, mode='passive')

    def hakrawler(self, domains):
        self.run_tool('hakrawler', domains, mode='active')

    def knockpy(self, domains):
        self.run_tool('knockpy', domains, mode='active')

    def shosubgo(self, domains):
        self.run_tool('shosubgo', domains, mode='passive')

    def shuffledns(self, domains):
        self.run_tool('shuffledns', domains, mode='active')

    def subdomainizer(self, domains):
        self.run_tool('subdomainizer', domains, mode='passive')

    def subfinder(self, domains):
        self.run_tool('subfinder', domains, mode='active')

    def waybackurls(self, domains):
        self.run_tool('waybackurls', domains, mode='passive')
