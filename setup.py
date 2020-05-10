#!/usr/bin/env python
# coding: utf-8

"""
WhatIsThisHere

Created: 03.05.20
"""

from setuptools import setup

setup(name='luechenbresse',
      version = '0.1',
      description = 'Scraping Germany',
      # url='http://github.com/storborg/funniest',
      # author='Flying Circus',
      # author_email='flyingcircus@example.com',
      license = 'MIT',
      packages = ['luechenbresse'],
      include_package_data = True,
      zip_safe = False,
#      test_suite = "luechenbresse.test",              # TODO: use tox
#      test_suite = "tests",
      scripts = ["bin/zdf-heute", "bin/luechenbresse"],
      install_requires = [
            'requests',
            'feedparser',
            'bs4',
            'docopt',
      ],
)