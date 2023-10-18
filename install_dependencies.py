#!/usr/bin/env python
import os
import traceback
import tarfile
import toml
import subprocess
import requests
import shutil
import distro
import sys

import common
from common import handle_error, get_api_keys
from zipfile import ZipFile


config_dir = os.path.expanduser('~/.config/recono-suite')
go_bin_path = os.path.expanduser('~/go/bin')
executable_dir = os.path.expanduser('~/.local/bin')
downloads_dir = os.path.expanduser('~/Downloads')
config_file = os.path.join(config_dir, 'config.toml')
configuration = {}


# region Initialization Functions
def initialize_file_structure_requirements():
    global configuration
    script_root = os.path.dirname(os.path.abspath(__file__))
    temp_subdom_master_path = os.path.join(script_root, 'wordlists', 'subdomain_master.txt')
    new_subdom_master_path = os.path.join(config_dir, 'subdomain_master.txt')
    profile_path = os.path.expanduser('~/.profile')
    path_line = f'export PATH="$PATH:{executable_dir}"'
    current_path_var = os.environ.get('PATH','').split(':')
    api_keys = get_api_keys(config_file)
    recon_dir = os.path.join(config_dir, 'recono-suite')
    configuration['api_keys'] = api_keys
    configuration['binary_paths'] = {
        'amass': os.path.join(executable_dir, 'amass'),
        'assetfinder': os.path.join(go_bin_path, 'assetfinder'),
        'bbot': os.path.join(executable_dir, 'bbot'),
        'github-subdomains': os.path.join(go_bin_path, 'github-subdomains'),
        'hakrawler': os.path.join(go_bin_path, 'hakrawler'),
        'knockpy': os.path.join(executable_dir, 'knockpy', 'knockpy.py'),
        'shosubgo': os.path.join(go_bin_path, 'shosubgo'),
        'shuffledns': os.path.join(go_bin_path,'shuffledns'),
        'subdomainizer': os.path.join(executable_dir, 'subdomainizer', 'SubDomainizer.py'),
        'subfinder': os.path.join(go_bin_path, 'subfinder'),
        'waybackurls': os.path.join(go_bin_path, 'waybackurls'),
    }
    configuration['wordlists'] = {
        'resolver_file': os.path.join(config_dir, 'wordlists', 'resolvers.txt'),
        'subdomain_wordlist': os.path.join(config_dir, 'wordlists', 'subdomain_master.txt')
    }

    if os.path.exists(config_dir):
        shutil.rmtree(config_dir)

    os.makedirs(executable_dir, exist_ok=True)
    os.makedirs(config_dir)

    # Move Wordlists into config_dir
    source_wordlists_path = os.path.join(script_root, 'wordlists')
    destination_wordlists_path = os.path.join(config_dir, 'wordlists')
    if os.path.exists(destination_wordlists_path):
        print(f'{destination_wordlists_path} already exists')
        shutil.rmtree(destination_wordlists_path)
    else:
        shutil.copytree(source_wordlists_path, destination_wordlists_path)
        print(f'Copied wordlists to {destination_wordlists_path}')

    # Initialize resolver file
    common.update_resolver_list(configuration)

    # Make sure executable_dir is in path
    if executable_dir not in current_path_var:
        try:
            with open(profile_path, 'a') as profile_file:
                profile_file.write(f'\n{path_line}')

            os.environ['PATH'] += f':{executable_dir}'
            print(f"Added {executable_dir} to PATH in {profile_path}")
        except Exception as e:
            handle_error(f'Could not add {executable_dir} to $PATH.', exception=e, prefix='Warning')

    # Create config file
    with open(config_file, 'w') as file:
        toml.dump(configuration, file)
    os.chmod(config_file, 0o600)
    print(f'Config File Created at {config_file}')
#endregion


#region Utility Functions
def shell_command_is_installed(cmd, override=''):
    if override:
        test_command = override.split()
    else:
        test_command = f'{cmd} --version'.split()
    try:
        subprocess.run(test_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return True
    except:
        return False



def get_shell_install_cmd(package):
    current_distro = distro.name().split()[0]
    install_cmd = ''
    package_manager_commands = {
        'Alpine': 'apk add',
        'Arch': 'pacman -S',
        'CentOS': 'yum install',
        'Clear Linux': 'swupd bundle-add',
        'Debian': 'apt-get install',
        'Fedora': 'dnf install',
        'Gentoo': 'emerge',
        'Mageia': 'urpmi',
        'Manjaro': 'pacman -S',
        'openSUSE': 'zypper install',
        'RedHat': 'yum install',
        'Slackware': 'slackpkg install',
        'Solus': 'eopkg it',
        'Ubuntu': 'apt install',
        'Void Linux': 'xbps-install -S'
    }
    try:
        install_cmd = f'sudo {package_manager_commands[current_distro]} {package}'
    except KeyError:
        print(f'Couldnt find the proper package manager for your distro. Please install {package}.')

    return install_cmd


def get_latest_github_release(releases_url, name):
    download_url = ''
    response = requests.get(releases_url)
    if response.status_code == 200:
        releases = response.json()
        if releases:
            if isinstance(releases, list):
                latest_release = releases[0]
                # print(latest_release)
                for asset in latest_release['assets']:
                    if name in asset['name']:
                        download_url = asset['browser_download_url']
            else:
                handle_error(f'A problem ocurred while trying to find the latest release at {releases_url}:\n')

    if not download_url:
        handle_error(f'A problem occurred while trying to find the latest release at {releases_url}')

    return download_url


def get_extracted_directory(url, extension):
    global downloads_dir
    extension = f'.{extension}'
    filename = url.split('/')[-1].replace(extension, '')
    return os.path.join(downloads_dir, filename)


def download_and_extract_tool(url, extension):
    extracted_tool_dir = get_extracted_directory(url, extension)
    extension = f'.{extension}'
    global downloads_dir
    downloaded_tool_path = os.path.join(downloads_dir, url.split('/')[-1])
    try:
        response = requests.get(url)
    except Exception as e:
        return handle_error(f'Could not download and extract {url}', exception=e)
    try:
        with open(downloaded_tool_path, 'wb') as file:
            file.write(response.content)
        match extension:
            case '.zip':
                with ZipFile(downloaded_tool_path, 'r') as zip_file:
                    zip_file.extractall(downloads_dir)
                    return True
            case '.tar.gz':
                with tarfile.open(downloaded_tool_path, 'r:gz') as tar_gz_file:
                    tar_gz_file.extractall(path=extracted_tool_dir)
                    return True
            case _:
                return handle_error(f'Unrecognized file type at {url}', ret=False)
    except Exception as e:
        return handle_error(f'Could not download tool from {url}, Please download manually.', exception=e)


def install_from_github(url, extension, binary_name):
    global executable_dir
    global downloads_dir

    extracted_dir = get_extracted_directory(url, extension)
    binary_path = os.path.join(extracted_dir, binary_name)
    out_path = configuration['binary_paths'][binary_name]
    if not download_and_extract_tool(url, extension):
        return False

    try:
        os.chmod(binary_path, 0o755)
        shutil.copy(binary_path, out_path)
        return True
    except FileNotFoundError as e:
        return handle_error(f'Binary {binary_name} is not in expected location. Please check your downloads folder and install binary to {out_path} manually.', exception=e)

def git_clone(url, name):
    out_path = os.path.dirname(configuration['binary_paths'][name])
    cmd = f'git clone {url} {out_path}'.split()

    if os.path.exists(out_path):
        shutil.rmtree(out_path)
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.chmod(configuration['binary_paths'][name], 0o755)
        return True
    except Exception as e:
        return handle_error(f'Problem occurred while cloning {url}. Please download manually and place in {executable_dir}', exception=e)


def install_shell_package(pkg):
    cmd = get_shell_install_cmd(pkg)
    if not cmd:
        return False
    try:
        result = subprocess.run(cmd, check=True, shell=True,stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        return handle_error(f'Something went wrong while installing {pkg}', exception=e)
    except Exception as e:
        return handle_error(f'Something went wrong while installing {pkg}', exception=e)


def go_install(pkg, override=''):
    if override:
        cmd = f'go {override} {pkg}'.split()
    else:
        cmd = f'go install -v {pkg}'.split()

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return True
    except Exception as e:
        return handle_error(f'Something went wrong while installing {pkg}', exception=e)
# endregion


#region Installation Functions
def install_pipx():
    try:
        subprocess.run(["pip", "install", "--user", "pipx"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["pipx", "ensurepath"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print('PipX successfully Installed')
        return True
    except Exception as e:
        return handle_error('Could not install PipX.', exception=e)


def install_go():
    result = install_shell_package('go')
    if result:
        print('Go Successfully Installed')
    return result


def install_amass():
    url = 'https://github.com/owasp-amass/amass/releases/download/v3.23.3/amass_Linux_amd64.zip'
    if install_from_github(url, 'zip', 'amass'):
        print(f'Amass successfully installed to {configuration["binary_paths"]["amass"]}')
        return True
    else:
        return handle_error('Amass Not installed', ret=False)


def install_assetfinder():
    url = 'github.com/tomnomnom/assetfinder@latest'
    out_path = configuration['binary_paths']['assetfinder']
    if go_install(url) and os.path.exists(out_path):
        print(f'AssetFinder successfully installed to {out_path}')
        return True
    else:
        return False


def install_bbot():
    cmd = 'pipx install bbot --force'.split()
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f'Bbot successfully installed to {configuration["binary_paths"]["bbot"]}')
        return True
    except Exception as e:
        return handle_error('Problem occurred while installing Bbot', e)


def install_github_subdomains():
    url = 'github.com/gwen001/github-subdomains@latest'
    out_path = configuration['binary_paths']['github-subdomains']
    if go_install(url) and os.path.exists(out_path):
        print(f'Github-Subdomains successfully installed to {out_path}')
        return True
    else:
        return False


def install_hakrawler():
    url = 'github.com/hakluke/hakrawler@latest'
    out_path = configuration['binary_paths']['hakrawler']
    if go_install(url) and os.path.exists(out_path):
        print(f'Hakrawler successfully installed to {out_path}')
        return True
    else:
        return False


def install_knockpy():
    url = 'https://github.com/guelfoweb/knock.git'
    name = 'knockpy'
    out_path = configuration['binary_paths']['knockpy']
    prereq_file = os.path.join(os.path.dirname(out_path), 'requirements.txt')
    prereq_cmd = f'pip install -r {prereq_file}'.split()
    setup_file = os.path.join(os.path.dirname(out_path), 'setup.py')
    setup_cmd = f'sudo python {setup_file} install'

    try:
        git_clone(url, name)
        print(f'Installing Knockpy requirements at {prereq_file}')
        subprocess.run(prereq_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f'Running setup file {setup_file}')
        subprocess.run(setup_cmd, check=True, shell=True, cwd=os.path.dirname(out_path), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f'Knockpy successfully installed to {out_path}')
        return True
    except Exception as e:
        return handle_error(f'Problem ocurred while installing Knockpy', exception=e)


def install_shosubgo():
    url = 'github.com/incogbyte/shosubgo@latest'
    out_path = configuration['binary_paths']['shosubgo']
    if go_install(url) and os.path.exists(out_path):
        print(f'Shosubgo successfully installed to {out_path}')
        return True
    else:
        return False


def install_shuffledns():
    url = 'github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest'
    out_path = configuration['binary_paths']['shuffledns']
    if go_install(url) and os.path.exists(out_path):
        print(f'ShuffleDNS successfully installed to {out_path}')
        return True
    else:
        return False


def install_subdomainizer():
    url = 'https://github.com/nsonaniya2010/SubDomainizer.git'
    name = 'subdomainizer'
    out_path = configuration['binary_paths']['subdomainizer']
    prereq_file = os.path.join(os.path.dirname(out_path), 'requirements.txt')
    prereq_cmd = f'pip install -r {prereq_file} -force'.split()
    try:
        git_clone(url, name)
        print(f'Installing requirments at {prereq_file}')
        subprocess.run(prereq_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f'SubDomainzer successfully installed to {out_path}')
        return True
    except Exception as e:
        return handle_error(f'Problem ocurred while installing SubDomainizer.', exception=e)


def install_subfinder():
    url = 'github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest'
    out_path = configuration['binary_paths']['subfinder']
    if go_install(url) and os.path.exists(out_path):
        print(f'SubFinder successfully installed to {out_path}')
        return True
    else:
        return False


def install_waybackurls():
    url = 'github.com/tomnomnom/waybackurls@latest'
    out_path = configuration['binary_paths']['waybackurls']
    if go_install(url) and os.path.exists(out_path):
        print(f'Waybackurls successfully installed to {out_path}')
        return True
    else:
        return False


def check_and_install(cmd, install_function, override=None):
    if not shell_command_is_installed(cmd, override=override):
        return install_function()
    return True


def install_shell_tools():
    script_root = script_root = os.path.dirname(os.path.abspath(__file__))
    test_wordlist = os.path.join(config_dir, 'wordlists', 'test_install.txt')
    test_domain = 'chinesehappiness.com'

    commands_to_check = [
        ('pipx', install_pipx, None),
        ('go', install_go, 'go version'),
        ('amass', install_amass, None),
        ('assetfinder', install_assetfinder, f'assetfinder --subs-only {test_domain}'),
        ('bbot', install_bbot, None),
        ('github-subdomains', install_github_subdomains,
         f'github-subdomains -d {test_domain} -q -raw -t {configuration["api_keys"]["GitHub"]}'),
        ('hakrawler', install_hakrawler, f'echo {test_domain} | hakrawler -d 1'),
        ('knockpy', install_knockpy, None),
        ('shosubgo', install_shosubgo, f'shosubgo -d {test_domain} -s {configuration["api_keys"]["Shodan"]}'),
        ('shuffledns', install_shuffledns, f'shuffledns -d {test_domain} -w {test_wordlist} -r {configuration["wordlists"]["resolver_file"]}'),
        ('subdomainizer', install_subdomainizer, None),
        ('subfinder', install_subfinder, None),
        ('waybackurls', install_waybackurls, None)
    ]

    required_commands = {}
    for command, install_func, override in commands_to_check:
        required_commands[command] = check_and_install(command, install_func, override)

    for command, status in required_commands.items():
        print(f"\n[{command}]:\n\t{'Installed' if status else 'Not Installed'}")
# endregion


def main():
    initialize_file_structure_requirements()
    install_shell_tools()


if __name__ == '__main__':
    main()
