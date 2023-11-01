#!/usr/bin/env python
import os
import tarfile
import toml
import subprocess
import requests
import shutil
import distro

from common import common
from common.common import handle_error, get_api_keys
from zipfile import ZipFile


config_dir = os.path.expanduser('~/.config/recono-suite')
go_bin_path = os.path.expanduser('~/go/bin')
executable_dir = os.path.expanduser('~/.bin')
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
    pipx_path = os.path.expanduser('~/.local/bin')
    path_line = f'export PATH="$PATH:{executable_dir}"'
    current_path_var = os.environ.get('PATH','').split(':')
    api_keys = get_api_keys(config_file)
    recon_dir = os.path.join(config_dir, 'recono-suite')
    configuration['api_keys'] = api_keys
    configuration['binary_paths'] = {
        'amass': os.path.join(executable_dir, 'amass'),
        'assetfinder': os.path.join(go_bin_path, 'assetfinder'),
        'bbot': os.path.join(pipx_path, 'bbot'),
        'github-subdomains': os.path.join(go_bin_path, 'github-subdomains'),
        'go': '/usr/bin/go',
        'pipx' : '/usr/bin/pipx',
        'hakrawler': os.path.join(go_bin_path, 'hakrawler'),
        'knockpy': os.path.join(pipx_path, 'knockpy'),
        'massdns': os.path.join(executable_dir, 'massdns'),
        'shosubgo': os.path.join(go_bin_path, 'shosubgo'),
        'shuffledns': os.path.join(go_bin_path,'shuffledns'),
        'subdomainizer': os.path.join(pipx_path, 'subdomainizer'),
        'subfinder': os.path.join(go_bin_path, 'subfinder'),
        'waybackurls': os.path.join(go_bin_path, 'waybackurls'),
    }
    configuration['wordlists'] = {
        'resolver_file': os.path.join(config_dir, 'wordlists', 'resolvers.txt'),
        'subdomain_wordlist': os.path.join(config_dir, 'wordlists', 'subdomain_master.txt')
    }

    if os.path.exists(config_dir):
        shutil.rmtree(config_dir)

    if os.path.exists(executable_dir):
        if os.path.isdir(executable_dir):
            shutil.rmtree(executable_dir)
        elif os.path.exists(executable_dir):
            os.remove(executable_dir)

    os.mkdir(executable_dir)
    os.mkdir(config_dir)

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
def shell_command_is_installed(cmd):
    return os.path.exists(configuration['binary_paths'][cmd])



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
    out_path = os.path.join(downloads_dir, name)
    cmd = f'/usr/bin/git clone {url} {out_path}'.split()

    if os.path.exists(out_path):
        shutil.rmtree(out_path)
    try:
        subprocess.run(cmd, cwd=downloads_dir, env=os.environ, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git clone failed with error code {e.returncode}. Error message: {e.stderr.decode('utf-8')}")
        return handle_error(f'Problem occurred while cloning {url}. Please download manually and place in {executable_dir}', exception=e)
    except Exception as e:
        return handle_error(f'Problem occurred while cloning {url}. Please download manually and place in {executable_dir}', exception=e)


def git_make(url, name, binary_location):
    temp_out_path = common.make_temp_folder([url, name])
    out_path = configuration['binary_paths'][name]
    git_cmd = f'git clone {url} {temp_out_path}'.split()
    make_cmd = ['make']
    if os.path.exists(temp_out_path):
        shutil.rmtree(temp_out_path)
    try:
        subprocess.run(git_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        return handle_error(f'Problem occurred while cloning {url}. Please download manually and place in {executable_dir}', exception=e)

    # Time to make the binary, and move it to out_path
    os.chdir(temp_out_path)
    try:
        subprocess.run(make_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.run('sudo make install'.split(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        return handle_error(f'Problem occurred while making the {name} executable. Please check the build process.', exception=e)

    try:
        if os.path.exists(out_path):
            if os.path.isdir(out_path):
                shutil.rmtree(out_path)
            else:
                os.remove(out_path)
        shutil.move(os.path.join(temp_out_path, binary_location), out_path)
    except Exception as e:
        return handle_error(f'Problem occurred while moving the binary to {out_path}.', exception=e)

    shutil.rmtree(temp_out_path)
    return True


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
    working_dir = os.path.expanduser("~")
    if override:
        cmd = f'go {override} {pkg}'.split()
    else:
        cmd = f'go install -v {pkg}'.split()

    try:
        subprocess.run(cmd, check=False, cwd=working_dir, env=os.environ, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    print('\nInstalling Amass...')
    url = 'https://github.com/owasp-amass/amass/releases/download/v3.23.3/amass_Linux_amd64.zip'
    if install_from_github(url, 'zip', 'amass'):
        print(f'\tAmass successfully installed to {configuration["binary_paths"]["amass"]}')
        return True
    else:
        return handle_error('Amass Not installed', ret=False)


def install_assetfinder():
    print('\nInstalling AssetFinder...')
    url = 'github.com/tomnomnom/assetfinder@latest'
    out_path = configuration['binary_paths']['assetfinder']
    if go_install(url) and os.path.exists(out_path):
        print(f'\tAssetFinder successfully installed to {out_path}')
        return True
    else:
        return False


def install_bbot():
    print('\nInstalling Bbot...')
    cmd = 'pipx install bbot --force'.split()
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f'\tBbot successfully installed to {configuration["binary_paths"]["bbot"]}')
        return True
    except Exception as e:
        return handle_error('Problem occurred while installing Bbot', e)


def install_github_subdomains():
    print('\nInstalling Github-Subdomains...')
    url = 'github.com/gwen001/github-subdomains@latest'
    out_path = configuration['binary_paths']['github-subdomains']
    if go_install(url) and os.path.exists(out_path):
        print(f'\tGithub-Subdomains successfully installed to {out_path}')
        return True
    else:
        return False


def install_hakrawler():
    print('\nInstalling Hakrawler...')
    url = 'github.com/hakluke/hakrawler@latest'
    out_path = configuration['binary_paths']['hakrawler']
    if go_install(url) and os.path.exists(out_path):
        print(f'\tHakrawler successfully installed to {out_path}')
        return True
    else:
        return False


def install_knockpy():
    print('\nInstalling Knockpy...')
    url = 'https://github.com/guelfoweb/knock.git'
    name = 'knockpy'
    downloads_path = os.path.join(downloads_dir, name)
    setup_cmd = f'pipx install --force {downloads_path} '.split()

    try:
        git_clone(url, name)
        subprocess.run(setup_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f'\tKnockpy successfully installed')
        return True
    except Exception as e:
        return handle_error(f'Problem ocurred while installing Knockpy', exception=e)


def install_massdns():
    print('\tInstalling MassDNS...')
    url = 'https://github.com/blechschmidt/massdns.git'
    out_path = configuration['binary_paths']['massdns']
    if git_make(url, 'massdns', 'bin/massdns' ) and os.path.exists(out_path):
        print(f'\t\tMassDNS successfully insatalled to {out_path}')
        return True
    else:
        return False


def install_shosubgo():
    print('\nInstalling Showsubgo...')
    url = 'github.com/incogbyte/shosubgo@latest'
    out_path = configuration['binary_paths']['shosubgo']
    if go_install(url) and os.path.exists(out_path):
        print(f'\tShosubgo successfully installed to {out_path}')
        return True
    else:
        return False


def install_shuffledns():
    print('\nInstalling ShuffleDNS...')
    url = 'github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest'
    out_path = configuration['binary_paths']['shuffledns']
    common.update_resolver_list(configuration)
    if install_massdns():
        go_installed = go_install(url)
        outpath_exists = os.path.exists(out_path)
        if go_installed and outpath_exists:
            print(f'\tShuffleDNS successfully installed to {out_path}')
            return True
        else:
            return False
    else:
        return False


def install_subdomainizer():
    print(f'\nInstalling Subdomainizer...')
    url = 'https://github.com/TH3-F001/SubDomainizer.git'
    name = 'subdomainizer'
    downloads_path = os.path.join(downloads_dir, name)
    setup_cmd = f'pipx install --force  {downloads_path}'

    try:
        git_clone(url, name)
        result = subprocess.run(setup_cmd, check=True, cwd=downloads_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ)
        print(f'\tSubDomainzer successfully installed.')
        return True
    except Exception as e:
        return handle_error(f'Problem ocurred while installing SubDomainizer.', exception=e)


def install_subfinder():
    print('\nInstalling SubFinder...')
    url = 'github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest'
    out_path = configuration['binary_paths']['subfinder']
    if go_install(url) and os.path.exists(out_path):
        print(f'\tSubFinder successfully installed to {out_path}')
        return True
    else:
        return False


def install_waybackurls():
    print('\nInstalling WaybackURLs...')
    url = 'github.com/tomnomnom/waybackurls@latest'
    out_path = configuration['binary_paths']['waybackurls']
    if go_install(url) and os.path.exists(out_path):
        print(f'\tWaybackURLs successfully installed to {out_path}')
        return True
    else:
        return False


def check_and_install(cmd, install_function):
    if not shell_command_is_installed(cmd):
        return install_function()
    return True


def install_shell_tools():
    script_root = script_root = os.path.dirname(os.path.abspath(__file__))
    test_wordlist = os.path.join(config_dir, 'wordlists', 'test_install.txt')
    test_domain = 'chinesehappiness.com'

    commands_to_check = [
        ('pipx', install_pipx),
        ('go', install_go),
        ('amass', install_amass),
        ('assetfinder', install_assetfinder),
        ('bbot', install_bbot),
        ('github-subdomains', install_github_subdomains),
        ('hakrawler', install_hakrawler),
        ('knockpy', install_knockpy),
        ('shosubgo', install_shosubgo),
        ('shuffledns', install_shuffledns),
        ('subdomainizer', install_subdomainizer),
        ('subfinder', install_subfinder),
        ('waybackurls', install_waybackurls)
    ]

    required_commands = {}
    for command, install_func in commands_to_check:
        required_commands[command] = check_and_install(command, install_func)

    print(f"{'Binary':<20} {'Path':<50} {'Installed'}")

    for binary, path in configuration['binary_paths'].items():
        exists = os.path.exists(path)
        print(f"{binary:<20} {path:<50} {exists}")


# endregion


def main():
    initialize_file_structure_requirements()
    install_shell_tools()


if __name__ == '__main__':
    main()
