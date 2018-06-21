"""Module for downloading data different 'CURRENT' nemweb dataset
(selected data sets from files from http://www.nemweb.com.au/Reports/CURRENT)

Module includes one main superclass for generic nemweb files, and a series of
subclasses for specfic datasets. Datasets included from `CURRENT` index page:
- TradingIS_Reports
- DispatchIS_Reports
- Dispatch_SCADA
- Next_Day_Dispatch (DISPATCH_UNIT_SOLUTION)
- Next_Day_Actual_Gen (METER_DATA_GEN_DUID)
- ROOFTOP_PV/ACTUAL
"""

from io import BytesIO
import datetime
import re
import requests
from nemweb import nemfile_reader, nemweb_sqlite

class NemwebCurrentFile:
    """superclass for handling 'CURRENT' nemweb files from http://www.nemweb.com.au
    Each subclass requires:
    - nemweb_name: the name of the dataset to be download (e.g. Dispatch_SCADA)
    - filename_pattern: a regex expression to match and a determine datetime from filename
     on nemweb. As example, for files in the Dispatch_SCADA dataset
     (e.g "PUBLIC_DISPATCHSCADA_201806201135_0000000296175732.zip") the regex
     file_patten is PUBLIC_DISPATCHSCADA_([0-9]{12})_[0-9]{16}.zip
     - the format of the string to strip the datetime from. From the above example, the
     match returns '201806201135', so the string is "%Y%m%d%H%M",
     - the list of tables to insert from each dataset. This is derived from the 2nd and
      3rd column in the nemweb dataset. For example, the 2nd column is in Dispatch_SCADA
      is "DISPATCH" and the 3rd is "SCADA_VALUE" and the name is "DISPATCH_UNIT_SCADA".
      Several datasets contain multiple tables."""

    def __init__(self):
        self.base_url = "http://www.nemweb.com.au"
        self.section = "Reports/CURRENT"
        self.nemweb_name = None
        self.file_pattern = None
        self.datetime_format = None
        self.tables = []

    def update_data(self):
        """Main method to process nemweb dataset
        - downloads the index page for the dataset
        - determines date to start downloading from
        - matches the start date against files in the index
        - inserts new files into database"""
        start_date = nemweb_sqlite.start_from(self.tables[0])
        page = requests.get("{0}/{1}/{2}/".format(self.base_url, self.section, self.nemweb_name))
        regex = re.compile("/{0}/{1}/{2}".format(self.section, self.nemweb_name, self.file_pattern))

        for match in regex.finditer(page.text):
            file_datetime = datetime.datetime.strptime(match.group(1), self.datetime_format)
            if file_datetime > start_date:
                print(file_datetime)
                nemfile = self.download(match.group(0))
                self.insert_tables(nemfile)

    def insert_tables(self, nemfile):
        """Inserts dataframe into relevant table"""
        for table in self.tables:
            dataframe = nemfile.__dict__[table].drop_duplicates().copy()
            nemweb_sqlite.insert(dataframe, table)

    def download(self, link):
        """Dowloads nemweb zipfile from link into memory as a byteIO object.
        nemfile object is returned from the byteIO object """
        response = requests.get("{0}{1}".format(self.base_url,link))
        zip_bytes = BytesIO(response.content)
        nemfile = nemfile_reader.load_nemfile(zip_bytes)
        return nemfile

class DispatchSCADA(NemwebCurrentFile):
    """subclass of NemwebCurrentFile for Dispatch SCADA dataset
    Dataset contains dispatch unit scada table"""
    def __init__(self):
        NemwebCurrentFile.__init__(self)
        self.nemweb_name = "Dispatch_SCADA"
        self.file_pattern = 'PUBLIC_DISPATCHSCADA_([0-9]{12})_[0-9]{16}.zip'
        self.datetime_format = "%Y%m%d%H%M"
        self.tables = ["DISPATCH_UNIT_SCADA"]

class TradingIS(NemwebCurrentFile):
    """subclass of NemwebCurrentFile for Trading IS reports dataset.
    Dataset contains trading (30min) price, regionsum and interconnectorres tables"""
    def __init__(self):
        NemwebCurrentFile.__init__(self)
        self.nemweb_name = "TradingIS_Reports"
        self.file_pattern = "PUBLIC_TRADINGIS_([0-9]{12})_[0-9]{16}.zip"
        self.datetime_format = "%Y%m%d%H%M"
        self.tables = ['TRADING_PRICE', 'TRADING_REGIONSUM', 'TRADING_INTERCONNECTORRES']

class RooftopPVActual(NemwebCurrentFile):
    """subclass of NemwebCurrentFile for Actual Rooftop PV dataset.
    Adata set contians rooftop actual table"""
    def __init__(self):
        NemwebCurrentFile.__init__(self)
        self.nemweb_name = "ROOFTOP_PV/ACTUAL"
        self.file_pattern = "PUBLIC_ROOFTOP_PV_ACTUAL_([0-9]{14})_[0-9]{16}.zip"
        self.datetime_format = "%Y%m%d%H%M00"
        self.tables = ['ROOFTOP_ACTUAL']

class NextDayActualGen(NemwebCurrentFile):
    """subclass of NemwebCurrentFile for Next Day Actual Gen
        Dataset contains meter data gen duid table"""
    def __init__(self):
        NemwebCurrentFile.__init__(self)
        self.nemweb_name = "Next_Day_Actual_Gen"
        self.file_pattern = "PUBLIC_NEXT_DAY_ACTUAL_GEN_([0-9]{8})_[0-9]{16}.zip"
        self.datetime_format = "%Y%m%d"
        self.tables = ['METER_DATA_GEN_DUID']

class DispatchIS(NemwebCurrentFile):
    """subclass of NemwebCurrentFile for Dispatch IS reports dataset.
    Dataset contains dispatch (5min) price, regionsum and interconnectorres tables"""
    def __init__(self):
        NemwebCurrentFile.__init__(self)
        self.nemweb_name = "DispatchIS_Reports"
        self.file_pattern = "PUBLIC_DISPATCHIS_([0-9]{12})_[0-9]{16}.zip"
        self.datetime_format = "%Y%m%d%H%M"
        self.tables = ['DISPATCH_PRICE', 'DISPATCH_REGIONSUM', 'DISPATCH_INTERCONNECTORRES']

class NextDayDispatch(NemwebCurrentFile):
    """subclass of NemwebCurrentFile for Next Day Dispatch dataset.
    Dataset contains as dispatch unit solution table"""
    def __init__(self):
        NemwebCurrentFile.__init__(self)
        self.nemweb_name = "Next_Day_Dispatch"
        self.file_pattern = "PUBLIC_NEXT_DAY_DISPATCH_([0-9]{8})_[0-9]{16}.zip"
        self.datetime_format = "%Y%m%d"
        self.tables = ['DISPATCH_UNIT_SOLUTION']

if __name__ == "__main__":
    for nemwebfile in [TradingIS, DispatchIS, DispatchSCADA]:
        NemwebFile = nemwebfile()
        NemwebFile.update_data()
