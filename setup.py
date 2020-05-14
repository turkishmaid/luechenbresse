#!/usr/bin/env python
# coding: utf-8

"""
Support setuptools.

Created: 03.05.20
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='luechenbresse',
    version = '0.0.4',
    description = 'Scraping Germany',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/turkishmaid/luechenbresse',
    author = 'Sara Ziner',
    # author_email = 'flyingcircus@example.com',
    license = 'MIT',
    packages = setuptools.find_packages(),
    include_package_data = True,
    zip_safe = False,
    scripts = [ "bin/luechenbresse" ],
    install_requires = [ 'requests', 'feedparser', 'bs4', 'docopt', ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)