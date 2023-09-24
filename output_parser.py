import json
from csv import DictReader
from glob import glob

def _list_file_to_list(file_path):
    with open(file_path, 'r') as file:
        result = [line.strip() for line in file if line.strip()]

    return result


import json

def _json_file_to_list(file_path, key_name, delimiter=None):
    result = []
    with open(file_path, 'r') as file:
        file_content = file.read()

    try:
        # Try to load the JSON as-is first
        data = json.loads(file_content)
    except json.JSONDecodeError:
        # If that fails, try to repair it
        try:
            repaired_json = '[' + file_content.replace('}\n{', '},{') + ']'
            data = json.loads(repaired_json)
        except json.JSONDecodeError as e:
            print(f'Failed Parsing JSON File: {file_path}\n{e}')
            return result

    if isinstance(data, list):
        for item in data:
            if key_name is None and isinstance(item, dict):
                result.extend(key.replace('*', '') for key in item.keys())
            elif key_name and key_name in item:
                value = item[key_name].replace('*', '')
                if delimiter and delimiter in value:
                    result.extend(val.replace('*', '') for val in value.split(delimiter))
                else:
                    result.append(value)
    elif isinstance(data, dict):
        result.extend(key.replace('*', '') for key in data.keys())

    return result




def subscraper_output_to_set(cmd_out_path):
    result = _list_file_to_list(cmd_out_path)
    return result


def subfinder_output_to_set(cmd_out_path):
    result = _json_file_to_list(cmd_out_path, 'host', delimiter='\n')
    return result


def subdomainizer_output_to_set(cmd_out_path):
    cloud_services_path = f"{cmd_out_path.split('.txt')[0]}_cloudservices.txt"
    cloud_services = _list_file_to_list(cloud_services_path)
    filtered_cloud_services = [x for x in cloud_services if cloud_services.count('.') >= 2]
    result = _list_file_to_list(cmd_out_path) + filtered_cloud_services

    return result


def shodan_output_to_set(cmd_out_path):
    with open(cmd_out_path, 'r') as file:
        content = file.read().strip()
    result = content.split(';')

    return result

def knockpy_output_to_set(cmd_out_path):
    json_files = glob(f'{cmd_out_path}/*.json')
    result = []
    for file in json_files:
        result.extend(_json_file_to_list(file, None))
    if '_meta' in result:
        result.remove('_meta')

    return result


def gobuster_output_to_set(cmd_out_path):
    lines = _list_file_to_list(cmd_out_path)
    result = []
    for line in lines:
        result.append(line.replace('Found: ', '').strip())

    return result


def github_output_to_set(cmd_out_path):
    result = _list_file_to_list(cmd_out_path)
    return result


def bbot_output_to_set(cmd_out_path):
    csv_files = glob(f'{cmd_out_path}/*/output.csv')
    result = []
    for file in csv_files:
        with open(file, 'r') as file:
            csv = DictReader(file)
            for row in csv:
                if row['Event type'].upper() == 'DNS_NAME':
                    result.append(row['Event data'])

    return result


def assetfinder_output_to_set(cmd_out_path):
    result = _list_file_to_list(cmd_out_path)
    return result


def amass_output_to_set(cmd_out_path):
    result = _json_file_to_list(cmd_out_path, 'name')
    return result


def crt_output_to_set(cmd_out_path):
    result = _json_file_to_list(cmd_out_path, 'name_value', delimiter='\n')
    result.extend(_json_file_to_list(cmd_out_path,'common_name', delimiter='\n'))
    return result

def c99_output_to_set(cmd_out_path):
    result = _list_file_to_list(cmd_out_path)
    return result

def get_domain_output(cmd_out_directory, domain):
    result = []

    c99_file = f'{cmd_out_directory}/c99_{domain}.txt'
    crt_file = f'{cmd_out_directory}/crt-sh_{domain}.json'
    github_file = f'{cmd_out_directory}/github-subdomains_{domain}.txt'
    shodan_file = f'{cmd_out_directory}/shodan_{domain}.txt'
    assetfinder_file = f'{cmd_out_directory}/assetfinder_{domain}.txt'
    knockpy_dir = f'{cmd_out_directory}'
    subdomainizer_file = f'{cmd_out_directory}/subdomainizer_{domain}.txt'
    subscraper_file = f'{cmd_out_directory}/subscraper_{domain}.txt'
    subfinder_file = f'{cmd_out_directory}/subfinder_{domain}.json'
    gobuster_file = f'{cmd_out_directory}/gobuster_{domain}.txt'
    bbot_dir = f'{cmd_out_directory}/bbot_{domain}'
    amass_file = f'{cmd_out_directory}/amass_{domain}.json'

    result.extend(c99_output_to_set(c99_file))
    result.extend(crt_output_to_set(crt_file))
    result.extend(github_output_to_set(github_file))
    result.extend(shodan_output_to_set(shodan_file))
    result.extend(assetfinder_output_to_set(assetfinder_file))
    result.extend(knockpy_output_to_set(knockpy_dir))
    result.extend(subdomainizer_output_to_set(subdomainizer_file))
    result.extend(subscraper_output_to_set(subscraper_file))
    result.extend(subfinder_output_to_set(subfinder_file))
    result.extend(gobuster_output_to_set(gobuster_file))
    result.extend(bbot_output_to_set(bbot_dir))
    result.extend(amass_output_to_set(amass_file))

    return set(result)


def get_all_output(cmd_output_directory, domains):
    results = set()
    for domain in domains:
        results = results.union(get_domain_output(cmd_output_directory, domain))
    return results
