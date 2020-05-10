#!/usr/bin/env python
# coding: utf-8

"""
Convenience API for the ini file

Created: 09.05.20
"""

import os
import json
import configparser
from pathlib import Path

_CONFIG = None

def read():
    global _CONFIG
    if not _CONFIG:
        config_folder = Path(os.environ["HOME"]) / ".luechenbresse"
        ini_file = config_folder / "luechenbresse.ini"
        _CONFIG = configparser.ConfigParser()
        _CONFIG.read(ini_file)

def get(section, key, default=None):
    read()
    if section in _CONFIG:
        if key in _CONFIG[section]:
            return _CONFIG[section][key]
    return default

if __name__ == "__main__":
    pass