import os
import subprocess
import traceback

import toml
from bs4 import BeautifulSoup
import re
import requests


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


def get_config(config_file):
    return toml.load(config_file)

def get_asn(domain):
    url = f'https://www.robtex.com/dns-lookup/{domain}#records'
    response = requests.get(url).content
    soup = BeautifulSoup(response, 'html.parser')

    asn_link = soup.find('a', string=re.compile(r'AS\d{1,10}'))
    if asn_link:
        asn = asn_link.text.strip('AS')
        asname = soup.find('td', string='asname').find_next('td').text
        print(f'\n\nDomain:\t{domain}\nASN:\t{asn}\nName:\t{asname}\n\n')
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


def run(cmd):
    command = cmd.split(' ')
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')