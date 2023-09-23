import os
import toml
def get_lines_from_file(filename):
    result = []
    with open(filename, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line:
                result.append(stripped_line)
    return result

def get_api_keys(config_file=None):
    if config_file:
        api_keys = toml.load(config_file)["api_keys"]
        print(api_keys)
    else:
        api_keys = {'GitHub': os.environ.get('API_GITHUB') or input('Please provide your GitHub API key:\n> '),
                    'BeVigil': os.environ.get('API_BEVIGIL') or input('Please provide your BeVigil API key:\n> '),
                    'Censys': os.environ.get('API_CENSYS') or input('Please provide your Censys API key:\n> '),
                    'C99': os.environ.get('API_C99') or input('Please provide your C99 API key:\n> ')
                    }
    return api_keys