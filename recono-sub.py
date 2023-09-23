import argparse
import os
import hashlib
from multiprocessing import Pool
from threading import Thread
import common
from shell_commands import ShellCommand as ShellCmd

processed_domain_hashes = set()
config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.toml")

def parse_args():
    parser = argparse.ArgumentParser(description="Run recon tools with multiprocessing and threading.")

    parser.add_argument('-o', '--output', help='Output directory', required=True)

    domain_group = parser.add_mutually_exclusive_group(required=True)
    domain_group.add_argument('-d', '--domain', help='Single domain or comma-separated list of domains to process',
                              default=None)
    domain_group.add_argument('-dF', '--domain-file', help='File with a list of domains to process', default=None)

    args = parser.parse_args()

    if args.domain_file and not os.path.isfile(args.domain_file):
        parser.error(f"The file {args.domain_file} does not exist")

    return args


def extract_domains_from_input(args):
    domains = []
    if args.domain:
        domains = args.domain.split(',')
    elif args.domain_file:
        domains = common.get_lines_from_file(args.domain_file)

    return domains


def run_shell_commands_against_domain(domain, output_directory):
    shell_cmd = ShellCmd(domain, output_directory, config_file=config_file)

    threads = [
        Thread(target=shell_cmd.amass),
        Thread(target=shell_cmd.subfinder),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

############################################################
def hash_domain(domain):
    return hashlib.md5(domain.encode()).hexdigest()


def is_new_domain(domain):
    domain_hash = hash_domain(domain)
    if domain_hash in processed_domain_hashes:
        return False
    processed_domain_hashes.add(domain_hash)
    return True


def gather_new_domain_output(output_directory):
    #Parse output files and return list of new domains


def recursive_recon(domains, output_directory):
    new_domains = domains
    while new_domains:
        new_domains = run_recon(new_domains, output_directory)
        new_domains = gather_new_domain_output(output_directory)
###########################################################################


def run_recon(domains, output_directory):
    # Should return list of all found domains, so we'll need to throw our output parsing in here
    with Pool() as pool:
        cmd_args = []
        for domain in domains:
            cmd_args.append((domain, output_directory))

        pool.starmap(run_shell_commands_against_domain, cmd_args)



def main():
    args = parse_args()
    domains = extract_domains_from_input(args)
    output_directory = args.output

    run_recon()


    print(f"Output directory: {output_directory}")
    print(f"Domains: {domains}")


if __name__ == "__main__":
    main()
