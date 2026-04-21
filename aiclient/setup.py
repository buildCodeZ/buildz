#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Zzz(1309458652@qq.com)
# Description:

from setuptools import setup, find_packages,find_namespace_packages

setup(
    name = 'buildz_aiclient',
    version = '0.1.4',
    keywords='buildz',
    long_description=open('README.md', 'r', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    description = "用python写的ai客户端和ai技能管理工具, buildz包的一部分(buildz.aiclient)",
    license = 'Apache License 2.0',
    url = 'https://github.com/buildCodeZ/buildz',
    author = 'Zzz',
    author_email = '1309458652@qq.com',
    packages = find_namespace_packages(where="."),
    include_package_data = True,
    platforms = 'any',
    install_requires = ["openai", "ollama", "buildz>=0.9.35"],
)
