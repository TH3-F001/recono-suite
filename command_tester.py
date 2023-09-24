from shell_commands import ShellCommand
from output_parser import *
import os

output_directory = '/home/hanzo/Downloads/script_output'
config_file = os.path.expanduser("~/.config/recono-suite/config.toml")

cmd = ShellCommand('lacity.gov', output_directory, config_file)
cmd.c99_subdomain_finder()
#cmd.crt_sh()
# subfinder_file = f'{output_directory}/subfinder_lacity.gov.json'
# knockpy_file = f'{output_directory}/knockpy'
# amass_file = f'{output_directory}/amass_lacity.gov.json'
# crt_file = f'{output_directory}/crt-sh_lacity.gov.json'
# c99_file = f'{output_directory}/c99_lacity.gov.txt'
#
# subfinder_output = subfinder_output_to_set(subfinder_file)
# knockpy_output = knockpy_output_to_set(knockpy_file)
# amass_output = amass_output_to_set(amass_file)
# crt_output = crt_output_to_set(crt_file)
# c99_output = c99_output_to_set(c99_file)

for domain in get_all_output(output_directory, 'lacity.gov'):
    print(domain)
# json_generated_outputs = {'Subfinder': subfinder_output, 'Knockpy': knockpy_output, 'Amass': amass_output, 'CRT.sh': crt_output}
# json_generated_outputs = {'Amass': amass_output}
# json_generated_outputs = {'CRT.sh': crt_output}

# for cmd_name, output in json_generated_outputs.items():
#     print(f'\n{cmd_name}:')
#     print(output)
#     print(len(output))
#     for domain in output:
#         print(domain)

