#!/usr/bin/env python

"""
distutils/setuptools install script.
"""
import os
import re

from setuptools import setup, find_packages

ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')

def get_version():
    init = open(os.path.join(ROOT, 'hk_address_parser', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)

setup(
    name='hk-address-parser',
    version=get_version(),
    description='The Universal Python Library for HKAddressParser',
    long_description=open('README.md').read(),
    author='wingkwong',
    url='https://github.com/wingkwong/hk-address-parser',
    scripts=[],
    license="MIT",
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: MIT',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)