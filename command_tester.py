from shell_commands import ShellCommand
from output_parser import *
import os

output_directory = '/home/hanzo/Downloads/script_output'
config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.toml")
cmd = ShellCommand('lacity.gov',output_directory, config_file)

cmd.crt_sh()
subfinder_file = f'{output_directory}/subfinder_lacity.gov.json'
knockpy_file = f'{output_directory}/knockpy'
amass_file = f'{output_directory}/amass_lacity.gov.json'

subfinder_output = subfinder_output_to_set(subfinder_file)
knockpy_output = knockpy_output_to_set(knockpy_file)
amass_output = amass_output_to_set(amass_file)

json_generated_outputs = {'Subfinder': subfinder_output, 'Knockpy': knockpy_output, 'Amass': amass_output}
# json_generated_outputs = {'Amass': amass_output}
for cmd_name, output in json_generated_outputs.items():
    print(f'\n{cmd_name}:')
    print(output)

