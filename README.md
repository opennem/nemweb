# nemweb
This is a python3 package to directly download and process AEMO files from
[www.nemweb.com.au](https://www.nemweb.com.au/). Main module within the package
downloads the [nemweb](https://www.nemweb.com.au/) files and inserts the tables
into a local [SQLite](https://www.sqlite.org/) database.

This forms part of the backend of the
[OpenNEM](https://opennem.org.au/#/all-regions) platform. The OpenNEM backend
utilises a normalised [MySQL](https://www.mysql.com/) database (with foreign
key and unique constraints). At present, this package only includes a simple
sqlite interface without this support of capability. A mysql interface and
module will be added (...eventually - see
[enhancements](https://github.com/opennem/nemweb/issues?q=label%3Aenhancement)).

## Getting started

### Dependencies

*   [Python 3.6](https://www.python.org/downloads/)
*   [pip](https://pypi.org/project/pip/)
*   [SQLite](https://www.sqlite.org/)

### Installation

nemweb can be installed through `pip`:

```bash
pip install opennem
```

Or by running:

```bash
python3 setup.py install
```

From the package directory. If installing by setup.py, a post-install script
will prompt you input a directory for the sqlite database to live in. For
example:

```bash
'Enter directory (abs path) to store for sqlite db:'/home/dylan/Data
```

This value will live in a configuration file in your root directory
(`$HOME/.nemweb_config.ini`).

**IMPORTANT** If you install via `pip` you must manually enter the sqlite
directory in a file named `.nemweb_config.ini` in your home directly post-
install (...couldn't figure out how to make post-install scripts to work with
`pip`).

## Quick example

```python
from nemweb import nemweb_current

nemweb_current.update_datasets(['dispatch_scada'])
DISPATCH_UNIT_SCADA doesn't exists. Enter start date [YYYYMMDD]: 20180624
```

The first time you add a new dataset to you sqlite db, it will prompt you for a date to start donwloading from. From then on, it will only download data beyond what you already have locally.

You can chose to print progress to screen, if desired. For example (and for a table that has already been initialised):

```python
from nemweb import nemweb_current

nemweb_current.update_datasets(['dispatch_scada'], print_progress = True)
'Dispatch_SCADA 2018-06-24 13:40:00'
'Dispatch_SCADA 2018-06-24 13:45:00'
'Dispatch_SCADA 2018-06-24 13:50:00'
'Dispatch_SCADA 2018-06-24 13:55:00'
'...'
```

Currently, the following dataset are built in to the package, and can be added
and downloaded automatically from the
[`Current` index of nemweb](http://www.nemweb.com.au/Reports/Current/)

*   `next_day_actual_gen`
*   `rooftopPV_actual`
*   `trading_is`
*   `dispatch_scada`
*   `next_day_dispatch`
*   `dispatch_is`

Other datasets can be add by using using the class factory function for
containing data for 'Current' datasets (`CurrentDataset`) found in the
`nemweb_current` module.  The namedtuple from this can then be used with
`CurrentFileHandler` class to download and process that dataset.

## Documentation

![Build Status](https://readthedocs.org/projects/nemweb/badge/?version=latest)

Find more information in [the documentation at readthedocs](https://nemweb.readthedocs.io/en/latest/nemweb.html).

## TODO

In no particular order:

*   Add more datasets from [`Current` index](http://www.nemweb.com.au/Reports/Current/)
*   Add module to process archived data (from [`Archive` index](http://www.nemweb.com.au/Reports/ARCHIVE/))
*   Add more sophisticate support for sqlite database (e.g. selectively
    inserting fields, tables from dataset)
*   Add module for interfacing with mysql database
