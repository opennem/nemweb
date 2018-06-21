from . import config
import sqlite3
import os
import datetime


sqlite_dir = config['local_settings']['sqlite_dir']

def insert(df,table_name,db_name="nemweb_live.db"):
	with sqlite3.connect(os.path.join(sqlite_dir,db_name)) as conn:
		conn.execute("PRAGMA foreign_keys = ON")
		df.to_sql(table_name, con = conn, if_exists = 'append', index=None)
		conn.commit()
		
def table_latest_record(table_name,db_name="nemweb_live.db", timestamp_col="SETTLEMENTDATE"):
	with sqlite3.connect(os.path.join(sqlite_dir,db_name)) as conn:
		result = conn.execute("SELECT MAX({0}) FROM {1}".format(timestamp_col, table_name))
		date_str = result.fetchall()[0][0]
	return datetime.datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
	
def start_from(table_name,db_name="nemweb_live.db", timestamp_col="SETTLEMENTDATE"):
	try:
		d = table_latest_record(table_name,db_name=db_name, timestamp_col=timestamp_col)
	except sqlite3.OperationalError as E:
		msg = E.args[0].split(":")
		if msg[0] == 'no such table':
			date_str = input("{0} doesn't exists. Enter start date [YYYYMMDD]: ".format(msg[1]))
			d = datetime.datetime.strptime(date_str, "%Y%m%d")
		else:
			raise E
	return d
