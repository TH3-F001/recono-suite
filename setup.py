#!/usr/bin/env python
import os
import common
import toml
import subprocess
from setuptools import setup, find_packages


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
    config_dir = os.path.expanduser('~/.config/recono-suite')
    config_file = os.path.join(config_dir, 'config.toml')
    os.makedirs(config_dir, exist_ok=True)

    config = {}
    api_keys = common.get_api_keys(config_file)
    config['api_keys'] = api_keys


    with open(config_file, 'w') as file:
        toml.dump(config, file)


def pipx_is_installed():
    try:
        subprocess.run(['pipx', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False


def install_pipx():
    try:
        subprocess.run(["python3", "-m", "pip", "install", "--user", "pipx"], check=True)
        subprocess.run(["python3", "-m", "pipx", "ensurepath"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def bbot_is_installed():
    pass

def install_bbot():
    pass

def amass_is_installed():
    pass

def install_amass():
    pass

def gobuster_is_installed():
    pass

def install_gobuster():
    pass

def subfinder_is_installed():
    pass

def install_subfinder():
    pass

def subscraper_is_installed():
    pass

def install_subscraper():
    pass

def subdomainizer_is_installed():
    pass

def install_subdomainizer():
    pass

def knockpy_is_installed():
    pass

def install_knockpy():
    pass

def assetfinder_is_installed():
    pass

def install_assetfinder():
    pass

def github_subdomains_is_installed():
    pass

def install_github_subdomains():
    pass






def install_shell_tools():
    install_results = {}
    pipx_result = pipx_is_installed()

    if not pipx_result:
        pipx_result = install_pipx()

    install_results['pipx'] = pipx_result






def main():
    initialize_file_structure_requirements()


if __name__ == '__main__':
    main()
