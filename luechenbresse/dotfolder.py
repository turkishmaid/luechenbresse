#!/usr/bin/env python
# coding: utf-8

"""
Collect code that works with the files in teh .luechenbresse folder directly.

Created: 15.05.20
"""

import sys
import os
from pathlib import Path
import sqlite3
import logging
import logging.handlers
import configparser

from luechenbresse import data
from luechenbresse import __version__ as luechenbresse_version      # TODO gefällt mir nicht
from luechenbresse.mailgun import Mailgun

def _create_db(db_file, schema):
    # TODO support more than one schema per db
    if isinstance(schema, list):
        schema = schema[0]
    sql, _ = data.schema(schema)
    con = sqlite3.connect(db_file)
    cur = con.cursor()
    cur.executescript(sql)
    con.close()

def init_dotfolder(db_folder):
    # TODO move init() to module

    # create ~/.luechenbresse
    config_folder = Path(os.environ["HOME"]) / ".luechenbresse"
    logging.info(f"Configuration folder: {config_folder}")
    if config_folder.exists():
        logging.info(f"Configuration folder: {config_folder} OK")
    else:
        logging.info(f"Configuration folder: {config_folder} will be created")
        config_folder.mkdir()

    # create init-file
    ini_file = config_folder / "luechenbresse.ini"
    config = configparser.ConfigParser()
    if ini_file.exists():
        logging.info(f"Configuration file: {ini_file} OK")
    else:
        logging.info(f"Configuration file: {ini_file} will be created")
        ini_file.touch()

    config.read(ini_file)
    if not config.has_section("databases"):
        config.add_section("databases")

    # create database folder
    if not db_folder:
        db_folder = config_folder
        logging.info("Databases go into default location")
    else:
        db_folder = Path(db_folder).resolve()
        logging.info(f"Databases go into {db_folder}")

    if "folder" in config["databases"]:
        current_db_folder = config["databases"]["folder"]
        logging.info(f"Current folder for databases: {current_db_folder} - will be replaced")
    else:
        logging.info("No database location specified yet")

    logging.info(f"Setting database location to {db_folder}")
    config["databases"]["folder"] = str(db_folder)
    with open(ini_file, "w") as fp:
        config.write(fp)

    if db_folder.exists():
        logging.info("Using existing folder")
    else:
        logging.info(f"Creating {db_folder}...")
        db_folder.mkdir()

    feeds = data.feeds()
    for name in feeds:
        logging.info(f"Installing {name}")
        feed = feeds[name]
        db_file = db_folder / feed["db"]
        schema = feed["schema"]
        if db_file.exists():
            logging.info(f"Database {db_file} exists. LEAVING UNCHANGED")
        else:
            logging.info(f"Database {db_file} will be created with schema {schema}")
            # TODO: buffer schema
            _create_db(db_file, schema)


# TODO move LogManager to module where init() will live
class LogManager(object):
    """
    Set up logging and hold enough context to close the logfile for the current run and send contents via mail
    when all is set and done. A lalzada-Singleton.
    """

    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            FMT = "%(asctime)s [%(levelname)s] %(message)s"
            cls.instance = super().__new__(cls)
            self = cls.instance  # TODO scnr

            # default.log with 10 rotating segments of 100k each -> 1 MB (reicht viele Tage)
            log_file = Path(os.environ["HOME"]) / ".luechenbresse" / "default.log"
            rfh = logging.handlers.RotatingFileHandler(log_file, maxBytes=100_000, backupCount=10)
            rfh.setLevel(logging.INFO)

            # console output TODO switch off via ini-file
            sh = logging.StreamHandler(sys.stdout)
            sh.setLevel(logging.DEBUG)

            # file for output of the current run, will be sent via mail
            self.oneoff_file = Path(os.environ["HOME"]) / ".luechenbresse" / "current.log"
            self.fh = logging.FileHandler(self.oneoff_file, mode="w")
            self.fh.setLevel(logging.DEBUG)

            logging.basicConfig(level=logging.INFO, handlers=[rfh, sh, self.fh], format=FMT)
            logging.info("LogManager lebt.")
            logging.info(f"luechenbresse.__version__ = {luechenbresse_version}")  # TODO gefällt mir nicht

        return cls.instance

    def mail(self):
        # close current.log
        # https://stackoverflow.com/questions/15435652/python-does-not-release-filehandles-to-logfile
        logger = logging.getLogger()
        logger.removeHandler(self.fh)
        logging.info(f"closed ~/.luechenbresse/current.log")
        # send file contents via email
        # https://realpython.com/python-pathlib/#reading-and-writing-files
        subject = "von luechenbresse with love"
        body = self.oneoff_file.read_text()
        Mailgun().shoot(subject, body)


if __name__ == "__main__":
    pass