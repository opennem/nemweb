"""Initialises nemweb package, loads config"""
import configparser
import os

MODULE_DIR = os.path.dirname(__file__)
CONFIG = configparser.RawConfigParser()
CONFIG.read(os.path.join(MODULE_DIR, 'config.ini'))
