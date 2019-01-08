""" check that we download data the same as a saved pkl """

import os
import pkg_resources
import sqlite3
import datetime
import pytest

from nemweb import CONFIG
from nemweb.nemweb_current import CurrentFileHandler, DATASETS, update_datasets

from nemweb.utils import load_pickle, local_to_nem_tz


#setup = perhaps this could be turned into a fixture?
def test_nemweb():
    db_path = os.path.join(
        CONFIG['local_settings']['sqlite_dir'], 'test.db'
    )

    if os.path.exists(db_path):
        os.remove(db_path)
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

test_nemweb()

def test_table_creation():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    test_data = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    assert test_data == [('TRADING_PRICE',), ('TRADING_REGIONSUM',), ('TRADING_INTERCONNECTORRES',)]

#@pytest.mark.parametrize("section", CONFIG.sections())
def test_section_keys(table="TRADING_PRICE"):
    """checks keys data in tables (and lenth data matches expected data in trading interval)"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    return (cur.execute("SELECT count(*) FROM ='{0}'".format(table).fetchall()



