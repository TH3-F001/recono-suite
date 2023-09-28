#!/usr/bin/env python
import os
import zipfile
import tarfile
import common
import toml
import subprocess
import requests
import shutil
import distro
from zipfile import ZipFile
from setuptools import setup, find_packages


config_dir = os.path.expanduser('~/.config/recono-suite')
executable_dir = os.path.expanduser('~/.local/bin')
downloads_dir = os.path.expanduser('~/Downloads')
config_file = os.path.join(config_dir, 'config.toml')

# region Initialization Functions
def setup_python_requirements():
    script_root = os.path.abspath(__file__)
    requirements_path = os.path.join(script_root, 'requirements.txt')
    required_modules = []
    executables = [
        'recono-sub=recono_sub:main'
    ]
    entry_points = {
        'console_scripts': executables
    }

    with open(requirements_path, 'r') as file:
        for line in file:
            if line:
                required_modules.append(line.strip())

    print('Installing Requirements and Setting PATH')
    setup(
        name='Recono-Suite',
        version='0.1',
        packages=find_packages(),
        install_requires=required_modules,
        entry_points=entry_points
    )


def initialize_file_structure_requirements():
    global config_dir
    global config_file
    global executable_dir

    profile_path = os.path.expanduser('~/.profile')
    path_line = f'export PATH="$PATH:{executable_dir}'
    current_path_var = os.environ.get('PATH','').split(':')

    os.makedirs(config_dir, exist_ok=True)
    os.makedirs(executable_dir, exist_ok=True)

    if executable_dir not in current_path_var:
        with open(profile_path, 'a') as profile_file:
            profile_file.write*f'\n{path_line}'

        os.environ['PATH'] += f':{executable_dir}'
        print(f"Added {executable_dir} to PATH in {profile_path}")

    config = {}
    api_keys = common.get_api_keys(config_file)
    config['api_keys'] = api_keys

    with open(config_file, 'w') as file:
        toml.dump(config, file)
# endregion


# region Utility Functions


def shell_command_is_installed(cmd):
    try:
        subprocess.run([cmd, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False


def get_shell_install_cmd(package):
    current_distro = distro.name()[0]
    install_cmd = ''
    package_manager_commands = {
        'Alpine': 'sudo apk add',
        'Arch': 'sudo pacman -S',
        'CentOS': 'sudo yum install',
        'Clear Linux': 'sudo swupd bundle-add',
        'Debian': 'sudo apt-get install',
        'Fedora': 'sudo dnf install',
        'Gentoo': 'sudo emerge',
        'Mageia': 'sudo urpmi',
        'Manjaro': 'sudo pacman -S',
        'openSUSE': 'sudo zypper install',
        'RedHat': 'sudo yum install',
        'Slackware': 'sudo slackpkg install',
        'Solus': 'sudo eopkg it',
        'Ubuntu': 'sudo apt install',
        'Void Linux': 'sudo xbps-install -S'
    }
    try:
        install_cmd = package_manager_commands[current_distro]
    except KeyError:
        print('ERROR: Cannot determine linux distro. Are you using Windows you pleeb?')

    return install_cmd


def get_latest_github_release(releases_url, name):
    download_url = ''
    response = requests.get(releases_url)
    if response.status_code == 200:
        releases = response.json()
        print(type(releases))
        if releases:
            if isinstance(releases, list):
                latest_release = releases[0]
                # print(latest_release)
                for asset in latest_release['assets']:
                    if name in asset['name']:
                        download_url = asset['browser_download_url']
            # elif isinstance(releases, dict):
            #     for key in releases:
            #         if isinstance(releases[key], dict):
            #             print(f'\n\n{key}\n\t{releases[key]}')
            #     # for asset in releases['assets']:
            #     #     if name in asset['name']:
            #     #         download_url = asset['browser_download_url']
            else:
                print(f'ERROR: A problem ocurred while trying to find the latest release at {releases_url}:\n'
                      f'Response is neither dictionary nor list')

    if not download_url:
        print(f'ERROR: A problem occurred while trying to find the latest release at {releases_url}')

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
    response = requests.get(url)

    try:
        # Download the tar.gz file
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
                print(f'Unrecognized file type at {url}')
                return False
    except Exception as e:
        print(f'ERROR: Could not download tool from {url}, Please download manually. Error: {e}')
        return False


def install_from_github(url, extension, binary_name):
    global executable_dir
    global downloads_dir

    extracted_dir = get_extracted_directory(url, extension)
    binary_path = os.path.join(extracted_dir, binary_name)

    if not download_and_extract_tool(url, extension):
        return False

    try:
        os.chmod(binary_path, 0o755)
        shutil.copy(binary_path, executable_dir)
        return True
    except FileNotFoundError:
        print(f'ERROR: {binary_name} Binary is not in expected location. Please check your downloads folder and install binary to {executable_dir} manually.')

def install_shell_package(pkg):
    cmd = get_shell_install_cmd(pkg)
    try:
        result = subprocess.run(cmd.split(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f'Successfully Installed {pkg}')
        return True
    except subprocess.CalledProcessError as e:
        print(f'ERROR: Something went wrong while installing {pkg}')
        print(f"Error message: {e.stderr.decode('utf-8')}")
        return False


# endregion


#region Installation Checkers
def pipx_is_installed():
    return shell_command_is_installed('pipx')


def go_is_intsalled():
    return shell_command_is_installed('go')


def bbot_is_installed():
    return shell_command_is_installed('bbot')


def amass_is_installed():
    return shell_command_is_installed('amass')


def gobuster_is_installed():
    return shell_command_is_installed('gobuster')


def subfinder_is_installed():
    return shell_command_is_installed('subfinder')

def subscraper_is_installed():
    return shell_command_is_installed('subscraper')


def subdomainizer_is_installed():
    return shell_command_is_installed('subdomainizer')


def knockpy_is_installed():
    return shell_command_is_installed('knockpy')


def assetfinder_is_installed():
    return shell_command_is_installed('assetfinder')


def github_subdomains_is_installed():
    return shell_command_is_installed('github-subdomains')
# endregion


#region Installation Functions
def install_pipx():
    try:
        subprocess.run(["python3", "-m", "pip", "install", "--user", "pipx"], check=True)
        subprocess.run(["python3", "-m", "pipx", "ensurepath"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def install_go():
    return install_shell_package('go')


def install_bbot():
    try:
        subprocess.run(['pipx', 'install', 'bbot'])
        return True
    except subprocess.CalledProcessError:
        return False


def install_amass():
    url = 'https://github.com/owasp-amass/amass/releases/download/v3.23.3/amass_Linux_amd64.zip'
    return install_from_github(url, 'zip', 'amass')


def install_gobuster():
    url = get_latest_github_release('https://api.github.com/repos/OJ/gobuster/releases', 'gobuster_Linux_x86_64.tar.gz')
    return install_from_github(url, 'tar.gz', 'gobuster')


def install_subfinder():
    url = get_latest_github_release('https://api.github.com/repos/projectdiscovery/subfinder', 'linux_amd64.zip')
    return install_from_github(url, 'zip', 'subfinder')


def install_subscraper():
    pass


def install_subdomainizer():
    pass


def install_knockpy():
    pass


def install_assetfinder():
    pass


def install_github_subdomains():
    pass


def install_shell_tools():
    install_results = {}
    pipx_result = pipx_is_installed()

    if not pipx_result:
        pipx_result = install_pipx()

    install_results['pipx'] = pipx_result
# endregion

def main():
    # initialize_file_structure_requirements()
    # install_gobuster()
    # install_amass()
    # install_subfinder()
    print(distro.name())
if __name__ == '__main__':
    main()
