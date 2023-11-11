__package__ = 'recono_sub' 
import output_parser
from subdomain_tools import SubdomainRunner
import os
from common import common
import json

output_directory = '/home/neon/Downloads/recono-testing/results'
output_file = '/home/neon/Downloads/recono-testing/master_out.txt'
domains = common.get_lines_from_file('/home/neon/Downloads/recono-testing/test-domains.txt')
config_file = os.path.expanduser("~/.config/recono-suite/config.toml")
config = common.get_config(config_file)
print(json.dumps(config, indent=4))

cmd = SubdomainRunner(domains, output_directory, config)

cmd.amass()
cmd.assetfinder()
cmd.bbot()
cmd.c99_subdomain_finder()
cmd.crt_sh()
cmd.github_subdomains()
cmd.hakrawler()
cmd.knockpy()
cmd.shosubgo()
cmd.subdomainizer()
cmd.subfinder()
cmd.waybackurls()

results = sorted(output_parser.get_all_output(output_directory))

shuffle = SubdomainRunner(results, output_directory, config)
shuffle.shuffledns()

# with open(output_file, 'w') as file:
#     for result in results:
#         file.write(f'{str(result).strip(".")}\n')


