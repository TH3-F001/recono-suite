import json
from csv import DictReader
from glob import glob

def _list_file_to_list(file_path):
    with open(file_path, 'r') as file:
        result = [line.strip() for line in file if line.strip()]

    return result


def _json_file_to_list(file_path, key_name, delimiter=None):
    result = []
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Try to repair the bad JSON by making it an array of objects
    try:
        repaired_json = '[' + file_content.replace('}\n{', '},{') + ']'
        data = json.loads(repaired_json)
    except json.JSONDecodeError:
        print(f'Failed Parsing JSON File: {file_path}')
        return result

    for item in data:
        if key_name is None and isinstance(item, dict):
            result.extend(item.keys())
        elif key_name and key_name in item:
            value = item[key_name]
            if delimiter and delimiter in value:
                result.extend(value.split(delimiter))
            else:
                result.append(value)

    return result


def subscraper_output_to_set(cmd_out_path):
    result = _list_file_to_list(cmd_out_path)
    return set(result)


def subfinder_output_to_set(cmd_out_path):
    result = _json_file_to_list(cmd_out_path, 'host', delimiter='\n')
    return set(result)


def subdomainizer_output_to_set(cmd_out_path):
    cloud_services_path = f"{cmd_out_path.split('.txt')[0]}_cloudservices.txt"
    cloud_services = _list_file_to_list(cloud_services_path)
    filtered_cloud_services = [x for x in cloud_services if cloud_services.count('.') >= 2]
    result = _list_file_to_list(cmd_out_path) + filtered_cloud_services

    return set(result)


def shodan_output_to_set(cmd_out_path):
    with open(cmd_out_path, 'r') as file:
        content = file.read().strip()
    result = content.split(';')

    return set(result)

def knockpy_output_to_set(cmd_out_path):
    json_files = glob(f'{cmd_out_path}/*.json')
    result = []
    for file in json_files:
        result.extend(_json_file_to_list(file, None))
    if '_meta' in result:
        result.remove('_meta')

    return set(result)


def gobuster_output_to_set(cmd_out_path):
    lines = _list_file_to_list(cmd_out_path)
    result = []
    for line in lines:
        result.append(line.replace('Found: ', '').strip())

    return set(result)


def github_output_to_set(cmd_out_path):
    result = _list_file_to_list(cmd_out_path)
    return set(result)


def bbot_output_to_set(cmd_out_path):
    csv_files = glob(f'{cmd_out_path}/*/output.csv')
    result = []
    for file in csv_files:
        print(file)
        with open(file, 'r') as file:
            csv = DictReader(file)
            for row in csv:
                if row['Event type'].upper() == 'DNS_NAME':
                    result.append(row['Event data'])

    return set(result)

def assetfinder_output_to_set(cmd_out_path):
    result = _list_file_to_list(cmd_out_path)
    return set(result)

def amass_output_to_set(cmd_out_path):
    result = _json_file_to_list(cmd_out_path, 'name')
    return result

def crt_output_to_set(cmd_out_path):
    pass
    #result = _json_file_to_list(cmd_out_path,
