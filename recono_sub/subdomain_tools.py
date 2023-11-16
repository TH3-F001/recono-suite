__package__ = 'recono_sub'
import os
import requests
import json
from concurrent.futures import ThreadPoolExecutor
from common import common

from time import sleep
from random import uniform


class SubdomainRunner:
    def __init__(self, domains, output_dir, config, debug=False):
        self.out_dir = f'{os.path.abspath(output_dir)}/'
        self.config = config
        self.api_keys = config['api_keys']

        self.threads = 10
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.wordlist_path = os.path.join(script_dir, '../wordlists', 'subdomain_master.txt')
        os.makedirs(self.out_dir, exist_ok=True)
        self.debug = debug

    def run_tool(self, tool_name, domains, mode='passive'):
        if mode not in ['active', 'passive']:
            raise ValueError('Invalid mode. Mode must be either "active" or "passive')
        tool_config = self.config['tools'][tool_name]
        out_ext = tool_config.get('output_extenstion', '')
        out_ext = f'.{out_ext}' if out_ext else out_ext
        domain_arg_type = tool_config.get('domain_arg_type', '')
        cmd_arg_info = tool_config.get('run_command_args', {})

        shell_arg = bool(cmd_arg_info.get('shell', False))
        env_arg = os.environ if cmd_arg_info.get('env', '') == 'os.environ' else None
        cmd_requires_outpath = cmd_arg_info.get('out_path', False)

        if domain_arg_type in ['comma_separated', 'domain_file']:
            domain_input = ','.join(domains) if domain_arg_type == 'comma_separated' else common.make_temp_file(domains)
            domains_hash = common.hash_object(domains)
            out_path = os.path.join(self.out_dir, f'{tool_name}_{domains_hash}{out_ext}')
            supplemental_out_path = out_path if cmd_requires_outpath else None
            cmd = self.build_command(domain_input, out_path, mode)
            print(f'Running {tool_name.capitalize()}...')
            result = common.run_command(cmd, shell=shell_arg, env=env_arg, output_path=supplemental_out_path, debug=True)
        else:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                for domain in domains:
                    out_path = os.path.join(self.out_dir, f'{tool_name}_{domain}{out_ext}')
                    supplemental_out_path = out_path if cmd_requires_outpath else None
                    cmd = self.build_command(domain, out_path, mode)
                    executor.submit(common.run_command(cmd, shell=shell_arg, env=env_arg, output_path=supplemental_out_path, debug=True))

    def build_command(self, domain_input, out_path, mode):
        tool_config = self.config['tools']
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


    def amass(self, domains):
        domain_file = common.make_temp_file(domains)
        output_prefix = domain_file.split('/')[-1].split('_')[-2]
        out_path = os.path.join(self.out_dir, f'amass_{output_prefix}.json')
        amass_binary = self.config['tools']['amass']['binary_path']
        cmd = f'{amass_binary} enum -df {domain_file} -v -passive -json {out_path}'
        print(f'Running Amass against {domains}\n\tOutputting results to {out_path}')
        result = common.run_command(cmd, env=os.environ)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def assetfinder(self, domains):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_assetfinder, domains)

    def run_assetfinder(self, domain):
        out_path = os.path.join(self.out_dir, f'assetfinder_{domain}.txt')
        assetfinder_binary = self.config['tools']['assetfinder']['binary_path']
        cmd = f'{assetfinder_binary} --subs-only {domain}'
        print(f'Running AssetFinder against {domain}\n\tOutputting results to {out_path}')
        result = common.run_command(cmd, output_path=out_path, env=os.environ)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def bbot(self, domains):
        out_path = os.path.join(self.out_dir, f'bbot')
        domain_arg = ','.join(domains)
        bbot_binary = self.config['tools']['bbot']['binary_path']
        cmd = f'{bbot_binary} -t {domain_arg} -f subdomain-enum -o {out_path} -rf passive -y --no-deps'
        print(f'Running BBot against {domains}\n\tOutputting results to {out_path}')
        result = common.run_command(cmd, debug=True, env=os.environ)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

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
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_github_subdomains, domains)

    def run_github_subdomains(self, domain):
        out_path = os.path.join(self.out_dir, f'github-subdomains_{domain}.txt')
        github_subdomains_binary = self.config['tools']['github-subdomains']['binary_path']
        key = self.api_keys["GitHub"]
        cmd = f'{github_subdomains_binary} -e -d {domain} -t {key} -o {out_path}'
        print(f'Running GitHub against {domain}\n\tOutputting results to {out_path}')
        result = common.run_command(cmd, debug=True,env=os.environ)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def hakrawler(self, domains):
        domain_file = common.make_temp_file(domains)
        output_prefix = domain_file.split('/')[-1].split('_')[-2]
        out_path = os.path.join(self.out_dir, f'hakrawler_{output_prefix}.txt')
        hakrawler_binary = self.config['tools']['hakrawler']['binary_path']
        url_list = common.domains_to_urls(domains)
        url_file = common.make_temp_file(url_list)
        cmd = f'cat {url_file} | {hakrawler_binary} -subs'
        print(f'Running Hakrawler against {domains}\n\tOutputting results to {out_path}\n{cmd}')
        result = common.run_command(cmd, debug=True, output_path=out_path)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def knockpy(self, domains):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_knockpy, domains)

    def run_knockpy(self, domain):
        out_path = os.path.join(self.out_dir, f'knockpy_{domain}')
        knockpy_binary = self.config['tools']['knockpy']['binary_path']
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        cmd = f'{knockpy_binary} {domain} --no-http-code 404 -o {out_path} -th {self.threads}'

        print(f'Running KnockPy against {domain}\n\tOutputting results to {out_path}')
        result = common.run_command(cmd, debug=True)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def shuffledns(self, domains):
        common.update_resolver_list(self.config)

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_shuffledns, domains)

    def run_shuffledns(self, domain):
        out_path = os.path.join(self.out_dir, f'shuffledns_{domain}.txt')
        shuffledns_binary = self.config['tools']['shuffledns']['binary_path']
        wordlist_file = self.config['wordlists']['subdomain_wordlist']
        resolver_file = self.config['wordlists']['resolver_file']
        massdns_path = self.config['tools']['massdns']['binary_path']
        cmd = f'{shuffledns_binary} -d {domain} -w {wordlist_file} -r {resolver_file} -json -o {out_path} -m {massdns_path}'
        print(f'Running ShuffleDNS against {domain}\n\tOutputting results to {out_path}')
        result = common.run_command(cmd)


    def shosubgo(self, domains):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_shosubgo, domains)

    def run_shosubgo(self, domain):
        out_path = os.path.join(self.out_dir, f'shosubgo_{domain}.txt')
        shosubgo_binary = self.config['tools']['shosubgo']['binary_path']
        key = self.api_keys['Shodan']
        cmd = f'{shosubgo_binary} -d {domain} -s {key}'
        print(f'Running Shosubgo against {domain}\n\tOutputting results to {out_path}')
        result = common.run_command(cmd, output_path=out_path)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def subdomainizer(self, domains):
        domain_file = common.make_temp_file(domains)
        output_prefix = domain_file.split('/')[-1].split('_')[-2]
        out_path = os.path.join(self.out_dir, f'subdomainizer_{output_prefix}.txt')
        cloud_path = f'{self.out_dir}subdomainizer_{output_prefix}_cloudservices.txt'
        subdomainizer_binary = self.config['tools']['subdomainizer']['binary_path']
        github_key = self.api_keys["GitHub"]
        url_list = common.domains_to_urls(domains)
        temp_file = common.make_temp_file(url_list)
        cmd = f'{subdomainizer_binary} -l {temp_file} -g -gt {github_key} -o {out_path} -cop {cloud_path}'
        print(f'Running SubDomainizer against {domains}\n\tOutputting results to {out_path}')
        result = common.run_command(cmd)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def subfinder(self, domains):
        domain_file = common.make_temp_file(domains)
        output_prefix = domain_file.split('/')[-1].split('_')[-2]
        out_path = os.path.join(self.out_dir, f'subfinder_{output_prefix}')
        subfinder_binary = self.config['tools']['subfinder']['binary_path']
        temp_file = common.make_temp_file(domains)
        cmd = f'{subfinder_binary} -dL {temp_file} -all -oJ -o {out_path} -t {self.threads}'
        print(f'Running SubFinder against {domains}\n\tOutputting results to {out_path}')
        result = common.run_command(cmd, env=os.environ)
        # print(f'STDOUT: {stdout}\nSTDERR: {stderr}')

    def waybackurls(self, domains):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run_waybackurls, domains)

    def run_waybackurls(self, domain):
        out_path = os.path.join(self.out_dir, f'waybackurls_{domain}.txt')
        waybackurls_binary = self.config['tools']['waybackurls']['binary_path']
        cmd = f'echo {domain} | {waybackurls_binary}'
        print(f'Running Waybackurls against {domain}\n\tOutputting results to {out_path}')
        result = common.run_command(cmd, output_path=out_path)
        # print(f'STDOUT: {stdout}\nSTDERR
