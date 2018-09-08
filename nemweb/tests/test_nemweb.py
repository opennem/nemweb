""" check we can download a small amount of data """
import os
import sqlite3

from nemweb import CONFIG
from nemweb.nemweb_current import CurrentFileHandler, DATASETS, update_datasets


def test_nemweb():
    """ high level test of entire package functionality """

    handler = CurrentFileHandler()

    handler.update_data(DATASETS['trading_is'])

    db_path = os.path.join(
            CONFIG['local_settings']['sqlite_dir'], 'nemweb_live.db')

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")

    #  here I want to check the result versus a previously saved result
    #  this previously saved result will be package data
    #  just need to make sure the date selected is correct

    assert False
