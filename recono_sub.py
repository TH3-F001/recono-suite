import argparse
import os
from multiprocessing import Pool, Manager
from threading import Thread
import common
import output_parser
from subdomain_tools import SubdomainRunner as SubRunner


config_file = os.path.expanduser("~/.config/recono-suite/config.toml")
manager = Manager()
found_domain_results = manager.dict()
default_threads = 5

def parse_args():
    parser = argparse.ArgumentParser(description="Run recon tools with multiprocessing and threading.")

    parser.add_argument('-o', '--output', help='Output directory', required=True)
    parser.add_argument('-cF', '--config-file', help='Alternative config file. (see example-config.toml', required=False)
    parser.add_argument('-t', '--threads', help='Max number of concurrent domains to scan (default 5)')
    domain_group = parser.add_mutually_exclusive_group(required=True)
    domain_group.add_argument('-d', '--domain', help='Single domain or comma-separated list of domains to process',
                              default=None)
    domain_group.add_argument('-dF', '--domain-file', help='File with a list of domains to process', default=None)

    args = parser.parse_args()

    if args.domain_file and not os.path.isfile(args.domain_file):
        parser.error(f"The file {args.domain_file} does not exist")

    return args


def chunk_domains(domain_list, threads):
    total_domains = len(domain_list)
    chunk_size = total_domains // threads
    remainder = total_domains % threads
    chunks = []

    for i in range(0, total_domains - remainder, chunk_size):
        chunks.append(domain_list[i:i + chunk_size])

    for i in range(remainder):
        chunks[i].append(domain_list[-(i+1)])

    return chunks



def extract_domains_from_input(args):
    domains = []
    if args.domain:
        domains = args.domain.split(',')
    elif args.domain_file:
        domains = common.get_lines_from_file(args.domain_file)

    return domains


def run_shell_commands_against_domains(domains, output_directory, config, found_domains):

    shell_cmd = SubRunner(domains, output_directory, config)
    thread_targets = [
        shell_cmd.amass,
        shell_cmd.subfinder,
        shell_cmd.bbot,
        shell_cmd.subscraper,
        shell_cmd.subdomainizer,
        shell_cmd.knockpy,
        shell_cmd.assetfinder,
        shell_cmd.shosubgo,
        shell_cmd.hakrawler,
        shell_cmd.waybackurls,
        shell_cmd.github_subdomains,
        shell_cmd.c99_subdomain_finder,
        shell_cmd.crt_sh
    ]

    threads = []
    for target in thread_targets:
        print(f"Running {target.__name__} against {str(domains)}")  # Debug statement
        thread = Thread(target=target)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for domain in domains:
        found_domains[domain] = True


def run_recon(domains, config, found_domains, threads):
    unprocessed_domains = domains
    for domain in unprocessed_domains:
        if found_domains.get(domain, False):
            print(f'{domain} has already been processed, Skipping...')
            domains.remove(domain)
    domain_chunks = chunk_domains(domains, threads)
    output_directories = []
    for chunk in domain_chunks:
        output_directory = common.make_temp_folder(chunk)
        output_directories.append(output_directory)
        with Pool(processes=threads) as pool:
            cmd_args = [(chunk, output_directory, config, found_domains)]
            pool.starmap(run_shell_commands_against_domains, cmd_args)

    new_found_domains = set()
    for directory in output_directories:
        new_found_domains.extend(output_parser.get_all_output(directory, domains))

    for domain in new_found_domains:
        if domain not in found_domains:
            found_domains[domain] = False

    return dict(found_domains)


def main():
    global config_file
    args = parse_args()

    if args.threads:
        threads = int(args.threads)
    else:
        threads = default_threads

    if args.config_file:
        config_file = args.config_file
    config = common.get_config(config_file)
    domains = extract_domains_from_input(args)
    output_directory = args.output

    flat_results = run_recon(domains, config, found_domain_results, threads)

    # Write the results to a file in the output directory
    with open(os.path.join(output_directory, 'flat_results.txt'), 'w') as f:
        for domain, status in flat_results.items():
            f.write(f"{domain}\n")
            print(f'Found: {domain}')

    print(f"Output directory: {output_directory}")
    print(f"Domains: {domains}")


if __name__ == "__main__":
    main()

