# nemweb
This is a python3 package to directly download and process AEMO files from http://www.nemweb.com.au/. Main module within the package dowloads the nemweb files and inserts the tables with into a local sqlite database.

## quickstart

nemweb can be installed through `pip`:

```bash
pip install opennem
``` 

Or by running:

```bash
python3 setup.py install
```

From the package directory. If installing by setup.py, a post-install script will prompt you input a directory for the sqlite database to live in. For example:

```bash
Enter directory (abs path) to store for sqlite db:/home/dylan/Data
```

This value will live in a configuration file in your root directory (`$HOME/.nemweb_config.ini`). If you install via `pip` you must manually enter the directory post-install (...couldn't figure out how to make post-install scripts to work with `pip`). 
