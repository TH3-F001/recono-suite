__package__ = 'recono_sub'
import json
from csv import DictReader
from glob import glob
import os
from urllib.parse import urlparse
from common import common


def _list_file_to_list(file_path):
    with open(file_path, 'r') as file:
        result = [line.strip() for line in file if line.strip()]

    return result


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


def subfinder_output_to_set(cmd_out_path):
    result = _json_file_to_list(cmd_out_path, 'host', delimiter='\n')
    return result


def subdomainizer_output_to_set(cmd_out_path):
    if 'cloudservices' in cmd_out_path:
        cloud_services = common.get_lines_from_file(cmd_out_path)
        filtered_cloud_services = [x for x in cloud_services if cloud_services.count('.') >= 2]
        return cloud_services
    else:
        return common.get_lines_from_file(cmd_out_path)


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

def hakrawler_output_to_set(cmd_out_path):
    raw_output = common.get_lines_from_file(cmd_out_path)
    results = []
    for url in raw_output:
        if url.count('.') > 1 and 'www' not in url:
            parsed_url = urlparse(url)
            if parsed_url.netloc:
                results.append(parsed_url.netloc.split('@')[-1].split(':')[0])
    return results


def waybackurls_output_to_set(cmd_out_path):
    raw_output = common.get_lines_from_file(cmd_out_path)
    results = []
    for url in raw_output:
        if url.count('.') > 1 and 'www' not in url:
            parsed_url = urlparse(url)
            if parsed_url.netloc:
                results.append(parsed_url.netloc.split('@')[-1].split(':')[0])
    return results



def shosubgo_output_to_set(cmd_out_path):
    result = _list_file_to_list(cmd_out_path)
    return result


def get_all_output(cmd_out_directory):
    result = []

    tool_patterns = {
        'amass': 'amass_*.json',
        'assetfinder': 'assetfinder_*.txt',
        'bbot': 'bbot_*',
        'c99': 'c99_*.txt',
        'crt-sh': 'crt-sh_*.json',
        'github-subdomains': 'github-subdomains_*.txt',
        'hakrawler': 'hakrawler_*.json',
        'knockpy': 'knockpy_*',
        'shosubgo': 'shosubgo_*.txt',
        'subdomainizer': 'subdomainizer_*.txt',
        'subfinder': 'subfinder_*.json',
        'waybackurls': 'waybackurls_*.txt'
    }

    for tool, pattern in tool_patterns.items():
        paths = glob(os.path.join(cmd_out_directory, pattern))
        for path in paths:
            match tool:
                case 'amass':
                    result.extend(amass_output_to_set(path))
                case 'assetfinder':
                    result.extend(assetfinder_output_to_set(path))
                case 'bbot':
                    result.extend(bbot_output_to_set(path))
                case 'c99':
                    result.extend(c99_output_to_set(path))
                case 'crt-sh':
                    result.extend(crt_output_to_set(path))
                case 'github-subdomains':
                    result.extend(github_output_to_set(path))
                case 'hakrawler':
                    result.extend(hakrawler_output_to_set(path))
                case 'knockpy':
                    result.extend(knockpy_output_to_set(path))
                case 'shosubgo':
                    result.extend(shosubgo_output_to_set(path))
                case 'subdomainizer':
                    result.extend(subdomainizer_output_to_set(path))
                case 'subfinder':
                    result.extend(subfinder_output_to_set(path))
                case 'waybackurls':
                    result.extend(waybackurls_output_to_set(path))
                case _:
                    print(f"Unknown tool: {tool}")
    result = set(map(str.lower, result))

    return set(result)

