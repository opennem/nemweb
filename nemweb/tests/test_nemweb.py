""" check that we download data the same as a saved pkl """

import os
import pkg_resources
import sqlite3
import datetime
import pytest

from nemweb import CONFIG
from nemweb.nemweb_current import CurrentFileHandler, DATASETS, update_datasets

from nemweb.utils import load_pickle, local_to_nem_tz

DB_PATH = os.path.join(
    CONFIG['local_settings']['sqlite_dir'], 'test.db')

#setup = perhaps this could be turned into a fixture?
def nemweb_current():

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print('removed previous test database')

    handler = CurrentFileHandler()

    #test latest previous trading_interval
    local_datetime = datetime.datetime.now()
    nemtime = local_to_nem_tz(local_datetime)
    start_datetime = nemtime - datetime.timedelta(0,1800)

    handler.update_data(
        DATASETS['trading_is'],
        print_progress=True,
        db_name='test.db',
        start_date = start_datetime
    )

nemweb_current()

def test_table_creation():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    test_data = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    assert test_data == [('TRADING_PRICE',), ('TRADING_REGIONSUM',), ('TRADING_INTERCONNECTORRES',)]
