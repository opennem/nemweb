import os
import configparser
from setuptools import setup
from setuptools.command.install import install

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
        create_config()
        install.run(self)

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        create_config()
        develop.run(self)

setup(name='nemweb',
      version='0.1',
      description="newweb file handler",
      long_description="",
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



