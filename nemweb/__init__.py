"""Initialises nemweb package, loads config"""
import configparser
import os

LOCAL_DIR = os.path.expanduser("~")
CONFIG = configparser.RawConfigParser()
CONFIG.read(os.path.join(LOCAL_DIR, '.nemweb_config.ini'))
