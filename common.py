import os
import subprocess
import traceback
import random
import time
import toml
import hashlib
import tempfile
from bs4 import BeautifulSoup
import re
import requests
import socket
from subprocess import Popen, PIPE


def get_lines_from_file(filename):
    result = []
    with open(filename, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line:
                result.append(stripped_line)
    return result


def get_api_keys(config_file=None):
    if config_file and os.path.exists(config_file):
        try:
            api_keys = toml.load(config_file)["api_keys"]
        except:
            print("Unable to retrieve api Keys. rebuilding config file")
            api_keys = get_api_keys()
            return api_keys
    else:
        api_keys = {
            'GitHub': os.environ.get('API_GITHUB') or input('Please provide your GitHub API key:\n> '),
            'BeVigil': os.environ.get('API_BEVIGIL') or input('Please provide your BeVigil API key:\n> '),
            'C99': os.environ.get('API_C99') or input('Please provide your C99 API key:\n> '),
            'Shodan': os.environ.get('API_SHODAN') or input('Please provide your Shodan API key:\n> '),
            'Censys': {
                'ID': os.environ.get('API_CENSYS_ID') or input('Please provide your Censys API ID :\n> '),
                'Secret': os.environ.get('API_CENSYS_ID') or input('Please provide your Censys API secret:\n> ')
            }
        }
    return api_keys


def update_resolver_list(config_dict):
    resolver_list_url = 'https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt'
    response = requests.get(resolver_list_url)
    resolver_file = config_dict['wordlists']['resolver_file']

    if response.status_code == 200:
        with open(resolver_file, 'w') as file:
            file.write(response.text)
        print(f'Updated resolvers at {resolver_file}')
    else:
        print(f'Couldnt fetch the resolver list from {resolver_list_url}')


def port_is_open(domain, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((domain, port))
    except socket.error:
        return False
    return True


def domains_to_urls(domain_list):
    url_list = []
    for domain in domain_list:
        if port_is_open(domain, 443):
            url_list.append(f'https://{domain}')
        elif port_is_open(domain, 80):
            url_list.append(f'http://{domain}')
    return url_list


def get_config(config_file):
    return toml.load(config_file)

def get_asn(domain, use_asn=''):
    url = f'https://www.robtex.com/dns-lookup/{domain}#records'
    response = requests.get(url).content
    soup = BeautifulSoup(response, 'html.parser')

    asn_link = soup.find('a', string=re.compile(r'AS\d{1,10}'))
    if asn_link:
        asn = asn_link.text.strip('AS')
        asname = soup.find('td', string='asname').find_next('td').text
        print(f'\n\nDomain:\t{domain}\nASN:\t{asn}\nName:\t{asname}\n\n')
        if use_asn != '':
            use_asn = input(f'Would you like to add this ASN to your scanning parameters? Y/N: ').strip().lower()
        if use_asn == 'y':
            print(f'Adding ASN {asn} to scanning parameters.')
        else:
            print('Running scan without ASN parameter\n')
            asn = None
    else:
        print(f'ASN for {domain} not found.')
        asn = None
        return asn


def handle_error(message: str, exception: Exception=None, ret: bool=True, prefix: str='ERROR'):
    print(f'[{prefix}]: {message}')
    if exception:
        traceback.print_exc()
        ret = False
    return ret


def make_temp_file(input_list):
    m = hashlib.sha1()
    m.update(str(input_list).encode('utf-8'))
    hash_str = m.hexdigest()

    temp_file = tempfile.NamedTemporaryFile(delete=False, prefix=f"recono-sub_{hash_str}_", suffix=".txt")

    with open(temp_file.name, 'w') as file:
        for item in input_list:
            file.write(f'{item}\n')

    return temp_file.name


def make_temp_folder(input_list):
    m = hashlib.sha1()
    m.update(str(input_list).encode('utf-8'))
    hash_str = m.digest()
    temp_dir = tempfile.mkdtemp(prefix = f'recono-sub_{hash_str}_')
    return temp_dir

def run(cmd, retries=5, shell=False):
    command = cmd.split(' ')
    for i in range(retries):
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
            if result.returncode != 0:
                    handle_error(f'"{cmd}" failed on attempt {i+1}: {result.stderr.decode("utf-8")}\nSTDERR: {result.stderr}\nSTDOUT: {result.stdout}')
                    sleep_time = random.uniform(0.1, 3)
                    time.sleep(sleep_time)
            else:
                print(f'{cmd} has completed successfully')
                return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')
        except Exception as e:
            handle_error(f'A problem occurred while trying to run the shell command: {cmd}', e)

    handle_error(f'{cmd} failed after {retries} attempts')
    return None,None





def run_pipeline(cmd, output_path=None, retries=5):
    commands = [c.strip() for c in cmd.split('|')]
    for i in range(retries):
        try:
            processes = []
            prev_stdout = None

            for command in commands:
                p = Popen(command.split(), stdin=prev_stdout, stdout=PIPE, stderr=PIPE)
                if prev_stdout:
                    prev_stdout.close()
                prev_stdout = p.stdout
                processes.append(p)

            stdout, stderr = processes[-1].communicate()

            for p in processes:
                p.wait()

            if any(p.returncode != 0 for p in processes):
                handle_error(f'"{cmd}" failed on attempt {i + 1}: {stderr.decode("utf-8")}\nSTDERR: {stderr}\nSTDOUT: {stdout}')
                sleep_time = random.uniform(0.1, 3)
                time.sleep(sleep_time)
            else:
                if output_path:
                    with open(output_path, 'wb') as f:
                        f.write(stdout)
                print(f'"{cmd}" has completed successfully')
                return stdout.decode('utf-8'), stderr.decode('utf-8')

        except Exception as e:
            handle_error(f'A problem occurred while trying to run the shell command: "{cmd}"', e)

    handle_error(f'"{cmd}" failed after {retries} attempts.')
    return None, None




