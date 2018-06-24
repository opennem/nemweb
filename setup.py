from setuptools import setup

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
          'requests',
          'nemweb'])
