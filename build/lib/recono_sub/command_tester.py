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

cmd = SubdomainRunner(output_directory, config)

# cmd.amass(domains)                                                    # 
# cmd.assetfinder(domains)                                              # 
# cmd.bbot(domains)                                                     # 
# cmd.c99_subdomain_finder(domains)                                     # 
# cmd.crt_sh(domains)                                                   # 
# cmd.github_subdomains(domains)                                        # 
# cmd.hakrawler(domains)                                                # 
# cmd.knockpy(domains)       # only works in the installation venv      # 
# cmd.shosubgo(domains)                                                 # 
cmd.subdomainizer(domains)                                            # 
# cmd.subfinder(domains)                                                # 
# cmd.waybackurls(domains)

# results = sorted(output_parser.get_all_output(output_directory))
#
# # shuffle = SubdomainRunner(output_directory, config)
# # shuffle.shuffledns(domains)
#
# with open(output_file, 'w') as file:
#     for result in results:
#         file.write(f'{str(result).strip(".")}\n')


