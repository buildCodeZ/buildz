#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Zzz(1309458652@qq.com)
# Description:

from setuptools import setup, find_packages

setup(
    name = 'buildz',
    version = '0.2.4',
    keywords='buildz',
    long_description=open('README.md', 'r', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    description = "a json-like file format's read and write code by python, and codes to read and product object from configure file in such format",
    license = 'Apache License 2.0',
    url = 'https://github.com/buildCodeZ/buildz',
    author = 'Zzz',
    author_email = '1309458652@qq.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = [],
)