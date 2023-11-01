from setuptools import setup, find_packages
import os

def main():
    script_root = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(script_root, 'requirements.txt')
    required_modules = []
    executables = ['recono-sub=recono_sub.recono_sub:main']
    entry_points = {'console_scripts': executables}

    with open(requirements_path, 'r') as file:
        for line in file:
            if line:
                required_modules.append(line.strip())
    setup(
        name='recono-suite',
        version='0.2',
        author='Th3_F001',
        description='A series of multi-threaded, multi-processed tools for automating bug bounty recon.',
        url='https://github.com/TH3-F001/recono-suite',
        packages=find_packages(),
        install_requires=required_modules,
        entry_points=entry_points,
        python_requires='>=3.10',
        keywords='recon, security, bounty, subdomains'
    )

if __name__ == '__main__':
    main()