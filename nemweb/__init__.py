"""Initialises nemweb package, loads config"""
import configparser
CONFIG = configparser.RawConfigParser()
CONFIG.read(os.path.join('/data/config.ini'))
