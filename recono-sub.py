import argparse
import os
from multiprocessing import Pool, Manager
from threading import Thread
import common
import output_parser
from shell_commands import ShellCommand as ShellCmd

manager = Manager()
found_domain_results = manager.dict()
config_file = os.path.expanduser("~/.config/recono-suite/config.toml")


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


def run_shell_commands_against_domain(domain, output_directory, api_keys):
    shell_cmd = ShellCmd(domain, output_directory, api_keys)

    if found_domain_results.get(domain, False):
        print(f'{domain} has already been processed, Skipping...')
        return
    threads = [
        Thread(target=shell_cmd.gobuster),
        Thread(target=shell_cmd.amass),
        Thread(target=shell_cmd.bbot),
        Thread(target=shell_cmd.subfinder),
        Thread(target=shell_cmd.subscraper),
        Thread(target=shell_cmd.subdomainizer),
        Thread(target=shell_cmd.knockpy),
        Thread(target=shell_cmd.assetfinder),
        Thread(target=shell_cmd.shodan),
        Thread(target=shell_cmd.github_subdomains),
        Thread(target=shell_cmd.c99_subdomain_finder),
        Thread(target=shell_cmd.crt_sh)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    found_domain_results[domain] = True


def run_recon(domains, output_directory, api_keys):
    with Pool() as pool:
        cmd_args = [(domain, output_directory, api_keys) for domain in domains]
        pool.starmap(run_shell_commands_against_domain, cmd_args)

    new_found_domains = output_parser.get_all_output(output_directory, domains)

    for domain in new_found_domains:
        if domain not in found_domain_results:
            found_domain_results[domain] = False

    return dict(found_domain_results)


def main():
    args = parse_args()
    api_keys = common.get_api_keys(config_file)
    domains = extract_domains_from_input(args)
    output_directory = args.output

    run_recon(domains, output_directory, api_keys)

    print(f"Output directory: {output_directory}")
    print(f"Domains: {domains}")


if __name__ == "__main__":
    main()
