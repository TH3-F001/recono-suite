import common
import output_parser
from subdomain_tools import SubdomainRunner
from output_parser import *
import os

output_directory = '/home/hanzo/Downloads/script_output'
output_file = '/home/hanzo/Downloads/script_output/master_out.txt'
domains = common.get_lines_from_file('/home/hanzo/Downloads/test.txt')
config_file = os.path.expanduser("~/.config/recono-suite/config.toml")
config = common.get_config(config_file)

cmd = SubdomainRunner(domains, output_directory, config)

# cmd.amass()
# cmd.assetfinder()
# cmd.bbot()
# cmd.c99_subdomain_finder()
# cmd.crt_sh()
# cmd.github_subdomains()
# cmd.hakrawler()
# cmd.knockpy()
# cmd.shosubgo()
# cmd.subdomainizer()
# cmd.subfinder()
# cmd.waybackurls()
# #
results = sorted(output_parser.get_all_output(output_directory))
with open(output_file, 'w') as file:
    for result in results:
        file.write(f'{str(result).strip(".")}\n')


