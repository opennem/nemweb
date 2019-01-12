import os
import configparser
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop

def create_config():
    local_dir = os.path.expanduser("~")
    config = configparser.ConfigParser()
     # get existing values if they exist
    fileName = os.path.join(local_dir, '.nemweb_config.ini')
    try:
        config.read_file(open(fileName))
        print("found existing config file: %s" % fileName)
    except (OSError, configparser.ParsingError):
        print("failed to read existing config file: %s" % fileName)
    if not config.has_section('local_settings'):
            config.add_section('local_settings') 
            print('added local_settings')
    try:
        old_sqlite_db_dir = config.get("local_settings","sqlite_dir")
    except configparser.NoOptionError:
        old_sqlite_db_dir = os.path.expanduser("~/NEMData/")
    sqlite_db_dir = input("Enter sqlite directory (abs path)[" + old_sqlite_db_dir + "]:")
    sqlite_db_dir = sqlite_db_dir or old_sqlite_db_dir
    print("set sqlite_dir to %s" % sqlite_db_dir)
    try:
        old_start_date = config.get("local_settings","start_date")
    except configparser.NoOptionError:
        old_start_date = "20090701" # oldest known NEM data date
    start_date = input("Enter start date to begin down loading from (YYYYMMDD):[" + old_start_date + "]:")
    start_date = start_date or old_start_date
    print("set start_date to %s" % start_date)
    config.set("local_settings","sqlite_dir",sqlite_db_dir)
    config.set("local_settings","start_date", start_date)
    with open(os.path.join(fileName), "w") as cfgfile:
        config.write(cfgfile)

class PostInstallCommand(install):
    """Post-installation for install mode."""
    def run(self):
        try:
            create_config()
        except:
            print("failed to create config file")
        install.run(self)

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        try:
            create_config()
        except:
            print("failed to create config file")
        develop.run(self)

setup(name='nemweb',
      version='0.1',
      description="newweb file handler",
      long_description="python package to directly download and process AEMO files from http://www.nemweb.com.au/ and inserts tables into a local sqlite database.",
      author='dylan',
      author_email='dylan@opennem.org.au',
      license='MIT',
      packages=['nemweb'],
      zip_safe=False,
      install_requires=[
          'pandas',
          'requests'],
      cmdclass={'install': PostInstallCommand,
                'develop': PostDevelopCommand},
      package_data={'nemweb': 'tests/2018_09_21.pkl'}
      )
