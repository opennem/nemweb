import os
import configparser
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop

def create_config():
    local_dir = os.path.expanduser("~")
    config = configparser.ConfigParser()
    config.add_section("local_settings")
    _dir = input("Enter directory (abs path) to store for sqlite db:")
    config.set("local_settings","sqlite_dir",_dir)
    with open(os.path.join(local_dir,".nemweb_config.ini"), "w") as cfgfile:
        config.write(cfgfile)

class PostInstallCommand(install):
    """Post-installation for install mode."""
    def run(self):
        try:
            create_config()
        except:
            pass
        install.run(self)

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        try:
            create_config()
        except:
            pass
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
                'develop': PostDevelopCommand})
