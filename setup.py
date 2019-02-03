import re
import sys
from setuptools import setup, find_packages

setup(
    name='port-knocker',
    version='1.0.0',
    author='Bianca Ploch',
    author_email='fyyree@gmail.com',
    description='A magic portknocker.',
    url='https://github.com/fyyree/magicportknocker',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'portknock-client=port_knocker.client.cli_client:main',
            'portknock-server=port_knocker.server.cli_server:main',
            'portknock-admin=port_knocker.server.cli_admin:main',
        ],
    },
    package_data={'': ['README.md']},
    include_package_data=True,
    install_requires=[
        "cryptography",
        "netstruct",
        "appdirs",
        "click",
        "terminaltables",
        "python-iptables",
        "elevate",
        "pathlib2"
    ]
)