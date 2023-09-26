import argparse
import os
from multiprocessing import Pool, Manager
from threading import Thread
import common
import output_parser
from shell_commands import ShellCommand as ShellCmd


config_file = os.path.expanduser("~/.config/recono-suite/config.toml")
manager = Manager()
found_domain_results = manager.dict()


def parse_args():
    parser = argparse.ArgumentParser(description="Run recon tools with multiprocessing and threading.")

    parser.add_argument('-o', '--output', help='Output directory', required=True)
    parser.add_argument('-aF', '--api-file', help='Alternative API file. (see example-config.toml', required=False)
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


def run_shell_commands_against_domain(domain, output_directory, api_keys, found_domains, asn):
    shell_cmd = ShellCmd(domain, output_directory, api_keys, asn)

    if found_domains.get(domain, False):
        print(f'{domain} has already been processed, Skipping...')
        return

    thread_targets = [
        shell_cmd.gobuster,
        shell_cmd.amass,
        shell_cmd.bbot,
        shell_cmd.subfinder,
        shell_cmd.subscraper,
        shell_cmd.subdomainizer,
        shell_cmd.knockpy,
        shell_cmd.assetfinder,
        shell_cmd.shodan,
        shell_cmd.github_subdomains,
        shell_cmd.c99_subdomain_finder,
        shell_cmd.crt_sh
    ]

    threads = []
    for target in thread_targets:
        print(f"Running {target.__name__} against {domain}")  # Debug statement
        thread = Thread(target=target)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    found_domains[domain] = True


def run_recon(domains, output_directory, api_keys, found_domains, asn_info):
    with Pool() as pool:
        cmd_args = [(domain, output_directory, api_keys, found_domains, asn_info[domain]) for domain in domains]
        pool.starmap(run_shell_commands_against_domain, cmd_args)

    new_found_domains = output_parser.get_all_output(output_directory, domains)

    for domain in new_found_domains:
        if domain not in found_domains:
            found_domains[domain] = False

    return dict(found_domains)

def main():
    global config_file
    args = parse_args()

    if args.api_file:
        config_file = args.api_file
    api_keys = common.get_api_keys(config_file)
    domains = extract_domains_from_input(args)
    output_directory = args.output

    asn_info = {}
    for domain in domains:
        asn = common.get_asn(domain)
        asn_info[domain] = asn

    flat_results = run_recon(domains, output_directory, api_keys, found_domain_results, asn_info)

    # Write the results to a file in the output directory
    with open(os.path.join(output_directory, 'flat_results.txt'), 'w') as f:
        for domain, status in flat_results.items():
            f.write(f"{domain}\n")
            print(f'Found: {domain}')

    print(f"Output directory: {output_directory}")
    print(f"Domains: {domains}")


if __name__ == "__main__":
    main()

