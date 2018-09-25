""" check that we download data the same as a saved pkl """

import os
import pkg_resources
import sqlite3

from nemweb import CONFIG
from nemweb.nemweb_current import CurrentFileHandler, DATASETS, update_datasets

from nemweb.utils import load_pickle


def test_nemweb():
    db_path = os.path.join(
        CONFIG['local_settings']['sqlite_dir'], 'test.db'
    )

    if os.path.exists(db_path):
        os.remove(db_path)
        print('removed previous test database')

    handler = CurrentFileHandler()

    handler.update_data(
        DATASETS['trading_is'], start_date='20180921', end_date='20180922',
        print_progress=True, db_name='test.db'
    )

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    test_data = cur.execute("SELECT RRP FROM TRADING_PRICE").fetchall()


    test_data_check = pkg_resources.resource_filename(
        'nemweb', 'tests/2018_09_21.pkl'
    )

    test_data_check = load_pickle(test_data_check)

    assert test_data == test_data_check
