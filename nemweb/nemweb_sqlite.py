""" interfaces with sqlite3 database """
import sqlite3
import os
import datetime
from nemweb import CONFIG


def insert(dataframe, table_name, db_name="nemweb_live.db"):
    """
    Inserts dataframe into a table (table name) in an sqlite3 database (db_name).
    Database directory needs to be specfied in config.ini file
    """
    db_path = os.path.join(CONFIG['local_settings']['sqlite_dir'], db_name)
    with sqlite3.connect(db_path) as conn:
        dataframe.to_sql(table_name, con=conn, if_exists='append', index=None)
        conn.commit()


def table_latest_record(
        table_name, db_name="nemweb_live.db", timestamp_col="SETTLEMENTDATE"
):
    """
    Returns the lastest timestamp from a table in an sqlite3 database
    as a datetime object.

    Timestamp fields in nemweb files usually named "SETTLEMENTDATE".
    Sometimes INTERVAL_DATETIME is used.
    """
    db_path = os.path.join(CONFIG['local_settings']['sqlite_dir'], db_name)
    with sqlite3.connect(db_path) as conn:
        result = conn.execute(
            "SELECT MAX({0}) FROM {1}".format(timestamp_col, table_name)
        )
        date_str = result.fetchall()[0][0]
    return datetime.datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')


def start_from(
        table_name,
        db_name="nemweb_live.db",
        timestamp_col="SETTLEMENTDATE"
):
    """
    Returns a date to start downloading data from.
    Tries determining latest date from table in database. On fail falls back to
    CONFIG file value. 
    """
    try:
        date = table_latest_record(
            table_name, db_name=db_name, timestamp_col=timestamp_col
        )

    except sqlite3.OperationalError as error:
        msg = error.args[0].split(":")
        if msg[0] == 'no such table':
            date_str = os.path.join(CONFIG['local_settings']['start_date'])
            date = datetime.datetime.strptime(date_str, "%Y%m%d")
        else:
            raise error

    return date
