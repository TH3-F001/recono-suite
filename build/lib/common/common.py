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
        print(f'\tUpdated resolvers at {resolver_file}')
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


def domains_to_urls(domains):
    url_list = []
    if isinstance(domains, str) and ',' in domains:
        domain_list = domains.split(',')
    elif isinstance(domains, str):
        domains_list = [domains]
    elif isinstance(domains, list):
        domains_list = domains
    else:
        raise ValueError("Cannot create url list. Invalid domains argument")
        return None

    for domain in domains:
            url_list.append(f'https://{domain}')
            url_list.append(f'http://{domain}')
    return url_list


def generate_url_file_from_domains(domains):
    if os.path.exists(domains):
        domain_list = []
        with open(domains) as file:
            for line in file.readlines():
                domain_list.append(line.replace('\n',''))
    else:
        domain_list = domains
    url_list = domains_to_urls(domain_list)
    file_path = make_temp_file(url_list)
    return file_path


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


def chunk_list(input_list, threads):
    total_elements = len(input_list)
    chunk_size = total_elements // threads
    remainder = total_elements % threads
    chunks = []

    for i in range(0, total_elements - remainder, chunk_size):
        chunks.append(input_list[i:i + chunk_size])

    for i in range(remainder):
        chunks[i].append(input_list[-(i+1)])

    return chunks


def handle_error(message: str, exception: Exception=None, ret: bool=True, prefix: str='ERROR'):
    print(f'[{prefix}]: {message}')
    if exception:
        traceback.print_exc()
        ret = False
    return ret


def indent_text(text, tab_count=2):
    tab = '\t'*tab_count
    return '\n'.join([tab + line for line in text.split('\n')]).rstrip()


def format_runtime(runtime):
    hours = int(runtime // 3600)
    minutes = int((runtime % 3600) // 60)
    seconds = runtime % 60
    return f"{hours} hours, {minutes} minutes, {seconds:.2f} seconds"


def get_runtime(start_time):
    end_time = time.time()
    run_time = end_time - start_time

    return format_runtime(run_time)



def make_temp_file(input_list):
    hash_str = hash_object(input_list)
    temp_file = tempfile.NamedTemporaryFile(delete=False, prefix=f"recono-sub_{hash_str}_", suffix=".txt")

    with open(temp_file.name, 'w') as file:
        for item in input_list:
            file.write(f'{item}\n')

    return temp_file.name


def make_temp_folder(input_list):
    hash_str = hash_object(input_list)
    temp_dir = tempfile.mkdtemp(prefix = f'recono-sub_{hash_str}_')
    return temp_dir


def hash_object(input_object):
    m = hashlib.md5()
    m.update(str(input_object).encode('utf-8'))
    return m.hexdigest()


def run_command(cmd, output_path=False, retries=5, shell=False, debug=True, env=None):
    commands = [c.strip() for c in cmd.split('|')]
    for i in range(retries):
        try:
            processes = []
            prev_stdout = None
            start_time = time.time()

            for command in commands:
                if shell:
                    input_command = command
                else:
                    input_command = command.split()

                p = subprocess.Popen(input_command, stdin=prev_stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell, env=env)
                if prev_stdout:
                    prev_stdout.close()
                prev_stdout = p.stdout
                processes.append(p)

            stdout, stderr = processes[-1].communicate()
            runtime = get_runtime(start_time)

            for p in processes:
                p.wait()

            last_process = processes[-1]
            result = {
                'stdin': cmd,
                'stdout': stdout.decode('utf-8'),
                'stderr': stderr.decode('utf-8'),
                'returncode': last_process.returncode,
                'runtime': runtime
            }

            if last_process.returncode != 0:
                handle_error(f'"{cmd}" failed on attempt {i + 1}: {stderr.decode("utf-8")}')
                sleep_time = random.uniform(0.1, 3)
                time.sleep(sleep_time)
            else:
                if output_path:
                    with open(output_path, 'wb') as f:
                        f.write(stdout)
                if debug:
                    indented_stdout = indent_text(result['stdout'])
                    indented_stderr = indent_text(result['stderr'])
                    print(f'\tCommand:\n\t\t{cmd}\n\tSTDOUT:\n{indented_stdout}\n\tSTDERR:\n{indented_stderr}\n\tRuntime:\n\t\t{runtime}\n\tReturn Code:\n\t\t{last_process.returncode}')
                print(f'\t"{cmd}" has completed successfully')
                return result

        except Exception as e:
            handle_error(f'A problem occurred while trying to run the shell command: "{cmd}"', e)

    handle_error(f'"{cmd}" failed after {retries} attempts.')
    return None


