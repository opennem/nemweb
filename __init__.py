import configparser
import os

module_dir = os.path.dirname(__file__)
config = configparser.RawConfigParser()
config.read(os.path.join(module_dir,'config.ini'))
