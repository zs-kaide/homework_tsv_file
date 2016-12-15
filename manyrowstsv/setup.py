#!/usr/bin/env python
# coding:utf-8

from setuptools import setup, find_packages


setup(
    name='zs.manyrowstsv',
    version='1.0.0',
    description='Python RandomRowsTsv_Project.',
    packages=find_packages(),
    include_packages_data=True,
    install_requires=[
        "click",
    ],

    entry_points="""
        [console_scripts]
        manyrowstsv = manyrowstsv:cmd
    """,
)
