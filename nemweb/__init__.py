"""Initialises nemweb package, loads config"""
import configparser
CONFIG = configparser.RawConfigParser()
CONFIG.read('/data/config.ini')
