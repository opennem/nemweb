"""Initialises nemweb package, loads config"""
import configparser
import os

CONFIG_DIR = "/nemweb/"
CONFIG = configparser.RawConfigParser()
CONFIG.read(os.path.join(CONFIG_DIR, 'config.ini'))
