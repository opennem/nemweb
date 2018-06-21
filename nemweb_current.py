from nemweb import nemfile_reader, nemweb_sqlite
import datetime
import requests
from io import BytesIO
import re

class NemwebCurrentFile:		
	def __init__(self):
		self.regex_pattern =  re.compile("/Reports/CURRENT/{0}/{1}".format(self.nemweb_name, self.file_pattern))
		self.page = requests.get("http://www.nemweb.com.au/Reports/CURRENT/{0}/".format(self.nemweb_name))

	def update_data(self):
		d = nemweb_sqlite.start_from(self.tables[0])	
		
		for match in self.regex_pattern.finditer(self.page.text):
			dt = datetime.datetime.strptime(match.group(1),self.datetime_format)
			if dt > d:
				print(dt)
				nemfile = self.load_from_zip(match.group(0))
				self.insert_tables(nemfile)
				
	def insert_tables(self,nemfile):
		for table in self.tables:
			df = nemfile.__dict__[table].drop_duplicates().copy()
			nemweb_sqlite.insert(df,table)				
	
	def load_from_zip(self,link):
		response = requests.get("http://www.nemweb.com.au{0}".format(link))
		zipIO = BytesIO(response.content)
		nemfile = nemfile_reader.load_nemfile(zipIO)
		return nemfile				

class DispatchSCADA(NemwebCurrentFile):		
	def __init__(self):
		self.nemweb_name = "Dispatch_SCADA"		
		self.file_pattern = 'PUBLIC_DISPATCHSCADA_([0-9]{12})_[0-9]{16}.zip'
		self.datetime_format = "%Y%m%d%H%M"
		self.tables = ["DISPATCH_UNIT_SCADA"]
		NemwebCurrentFile.__init__(self)
		
class TradingIS(NemwebCurrentFile):		
	def __init__(self):
		self.nemweb_name = "TradingIS_Reports"		
		self.file_pattern = "PUBLIC_TRADINGIS_([0-9]{12})_[0-9]{16}.zip"
		self.datetime_format = "%Y%m%d%H%M"
		self.tables = ['TRADING_PRICE','TRADING_REGIONSUM','TRADING_INTERCONNECTORRES']
		NemwebCurrentFile.__init__(self)
		
class RooftopPVActual(NemwebCurrentFile):		
	def __init__(self):
		self.nemweb_name = "ROOFTOP_PV/ACTUAL"		
		self.file_pattern = "PUBLIC_ROOFTOP_PV_ACTUAL_([0-9]{14})_[0-9]{16}.zip"
		self.datetime_format = "%Y%m%d%H%M00"
		self.tables = ['ROOFTOP_ACTUAL']
		NemwebCurrentFile.__init__(self)
		
class NextDayActual_Gen(NemwebCurrentFile):		
	def __init__(self):
		self.nemweb_name = "Next_Day_Actual_Gen"		
		self.file_pattern = "PUBLIC_NEXT_DAY_ACTUAL_GEN_([0-9]{8})_[0-9]{16}.zip"
		self.datetime_format = "%Y%m%d"
		self.tables = ['METER_DATA_GEN_DUID']
		NemwebCurrentFile.__init__(self)			
		
class DispatchIS(NemwebCurrentFile):		
	def __init__(self):
		self.nemweb_name = "DispatchIS_Reports"		
		self.file_pattern = "PUBLIC_DISPATCHIS_([0-9]{12})_[0-9]{16}.zip"
		self.datetime_format = "%Y%m%d%H%M"
		self.tables = ['DISPATCH_PRICE','DISPATCH_REGIONSUM','DISPATCH_INTERCONNECTORRES']
		NemwebCurrentFile.__init__(self)		
		
class NextDayDispatch(NemwebCurrentFile):		
	def __init__(self):
		self.nemweb_name = "Next_Day_Dispatch"		
		self.file_pattern = "PUBLIC_NEXT_DAY_DISPATCH_([0-9]{8})_[0-9]{16}.zip"
		self.datetime_format = "%Y%m%d"
		self.tables = ['DISPATCH_UNIT_SOLUTION']
		NemwebCurrentFile.__init__(self)
			
				
if __name__ == "__main__":
	for nemwebfile in [TradingIS, DispatchIS, DispatchSCADA]:
		NemwebFile =  nemwebfile()
		NemwebFile.update_data()
