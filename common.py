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
    if config_file and os.path.exists(config_file):
        try:
            api_keys = toml.load(config_file)["api_keys"]
        except:
            print("Unable to retrieve api Keys. rebuilding config file")
            api_keys = get_api_keys()
            return api_keys
    else:
        api_keys = {
            'api_keys': {
                'GitHub': os.environ.get('API_GITHUB') or input('Please provide your GitHub API key:\n> '),
                'BeVigil': os.environ.get('API_BEVIGIL') or input('Please provide your BeVigil API key:\n> '),
                'C99': os.environ.get('API_C99') or input('Please provide your C99 API key:\n> '),
                'Censys': {
                    'ID': os.environ.get('API_CENSYS_ID') or input('Please provide your Censys API ID :\n> '),
                    'Secret': os.environ.get('API_CENSYS_ID') or input('Please provide your Censys API secret:\n> ')
                }
            }
        }
        config_dir = os.path.expanduser("~/.config/recono-suite")
        config_path = f'{config_dir}/config.toml'
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        with open(config_path, 'w') as file:
            toml.dump(api_keys, file)
        os.chmod(config_path, 0o600)

    return api_keys
