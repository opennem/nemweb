"""Module for downloading data different 'ARCHIVE' nemweb dataset
(selected data sets from files from http://www.nemweb.com.au/Reports/ARCHIVE)

Module includes one main superclass for handling generic nemweb archive files. A series of
namedtuples (strored in global constant DATASETS) contains the relevant data for specfic datasets.
Datasets included from 'ARCHIVE' index page:

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
from collections import namedtuple
import requests
from nemweb import nemfile_reader, nemweb_sqlite


class CurrentFileHandler:
    """class for handling 'ARCHIVE' nemweb files from http://www.nemweb.com.au
    Requires a 'CurrentDataset' namedtuple with following fields:

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

    Several datasets contain multiple tables. Examples can be found in the DATASETS dict
    (nemweb_reader.DATASETS)"""

    def __init__(self):
        self.base_url = "http://www.nemweb.com.au"
        self.section = "Reports/ARCHIVE"

    def update_data(
            self,
            dataset,
            print_progress=False,
            db_name='nemweb_archive.db',
            start_date = None
    ):
        """Main method to process nemweb dataset
        - downloads the index page for the dataset
        - determines date to start downloading from
        - matches the start date against files in the index
        - inserts new files into database"""
        if start_date == None:
            start_date = nemweb_sqlite.start_from(
                table_name=dataset.tables[0],
                timestamp_col=dataset.datetime_column,
                db_name=db_name
        )
        # get level 1 (L1) index page
        index_page = requests.get("{0}/{1}/{2}/".format(self.base_url,
                                                  self.section,
                                                  dataset.dataset_name))
        print(index_page)
        # build the regex pattern ready for the L1 index matching          
        regex_L1 = re.compile("/{0}/{1}/{2}".format(self.section,
                                                 dataset.dataset_name,
                                                 dataset.nemfile_L1_pattern))
        print(regex_L1)
        # build the regex pattern ready for the L2 index matching          
        regex_L2 = re.compile("{0}".format(dataset.nemfile_L2_pattern))

        for match in regex_L1.finditer(index_page.text):
            file_datetime = datetime.datetime.strptime(match.group(1), "%Y%m%d")
            if file_datetime > start_date:
                zip_bytes = self.download_zip(match.group(0))
                if print_progress:
                    print("Archive:", dataset.dataset_name, file_datetime)
                for filename, innerfile_zip in nemfile_reader.zip_streams(zip_bytes):
                    for match2 in regex_L2.finditer(filename):
                        file_datetime2 = datetime.datetime.strptime(match2.group(1), dataset.datetime_format)
                        innerfile = nemfile_reader.nemzip_reader(innerfile_zip)
                        if print_progress:
                            print(innerfile, file_datetime2)
                        for table in dataset.tables:
                            dataframe = innerfile[table].drop_duplicates().copy()
                            nemweb_sqlite.insert(dataframe, table, db_name)
            else:
                print("%s before %s, Skipping" % (start_date, file_datetime))

    def download_zip(self, link):
        """Dowloads nemweb zipfile from link into memory as a byteIO object.
        nemfile object is returned from the byteIO object """
        response = requests.get("{0}{1}".format(self.base_url, link))
        zip_bytes = BytesIO(response.content)
        # nemfile = nemfile_reader.nemzip_reader(zip_bytes)
        return zip_bytes




#  class factory function for containing data for 'Archive' datasets
ArchiveDataset = namedtuple("NemwebArchiveFile",
                            ["dataset_name",
                             "nemfile_L1_pattern",
                             "nemfile_L2_pattern",
                             "datetime_format",
                             "datetime_column",
                             "tables"])

DATASETS = {
    "dispatch_scada":ArchiveDataset(
        dataset_name="Dispatch_SCADA",
        nemfile_L1_pattern="PUBLIC_DISPATCHSCADA_([0-9]{8}).zip",
        nemfile_L2_pattern="PUBLIC_DISPATCHSCADA_([0-9]{12})_[0-9]{16}.zip",
        datetime_format="%Y%m%d%H%M",
        datetime_column="SETTLEMENTDATE",
        tables=["DISPATCH_UNIT_SCADA"]),

    "trading_is":    ArchiveDataset(
        dataset_name="TradingIS_Reports",
        nemfile_L1_pattern="PUBLIC_TRADINGIS_([0-9]{8})_[0-9]{8}.zip",
        nemfile_L2_pattern="PUBLIC_TRADINGIS_([0-9]{12})_[0-9]{16}.zip",
        datetime_format="%Y%m%d%H%M",
        datetime_column="SETTLEMENTDATE",
        tables=['TRADING_PRICE',
                'TRADING_REGIONSUM',
                'TRADING_INTERCONNECTORRES']),

    "rooftopPV_actual": ArchiveDataset(
        dataset_name="ROOFTOP_PV/ACTUAL",
        nemfile_L1_pattern="PUBLIC_ROOFTOP_PV_ACTUAL_([0-9]{8}).zip",
        nemfile_L2_pattern="PUBLIC_ROOFTOP_PV_ACTUAL_([0-9]{14})_[0-9]{16}.zip",
        datetime_format="%Y%m%d%H%M00",
        datetime_column="INTERVAL_DATETIME",
        tables=['ROOFTOP_ACTUAL']),

    "next_day_actual_gen": ArchiveDataset(
        dataset_name="Next_Day_Actual_Gen",
        nemfile_L1_pattern="NEXT_DAY_ACTUAL_GEN_([0-9]{8}).zip",
        nemfile_L2_pattern="PUBLIC_NEXT_DAY_ACTUAL_GEN_([0-9]{8})_[0-9]{16}.zip",
        datetime_format="%Y%m%d",
        datetime_column="INTERVAL_DATETIME",
        tables=['METER_DATA_GEN_DUID']),

    "dispatch_is": ArchiveDataset(
        dataset_name="DispatchIS_Reports",
        nemfile_L1_pattern="PUBLIC_DISPATCHIS_([0-9]{8}).zip",
        nemfile_L2_pattern="PUBLIC_DISPATCHIS_([0-9]{12})_[0-9]{16}.zip",
        datetime_format="%Y%m%d%H%M",
        datetime_column="SETTLEMENTDATE",
        tables=['DISPATCH_PRICE',
                'DISPATCH_REGIONSUM',
                'DISPATCH_INTERCONNECTORRES']),

    "next_day_dispatch": ArchiveDataset(
        dataset_name="Next_Day_Dispatch",
        nemfile_L1_pattern="PUBLIC_NEXT_DAY_DISPATCH_([0-9]{8}).zip",
        nemfile_L2_pattern="PUBLIC_NEXT_DAY_DISPATCH_([0-9]{8})_[0-9]{16}.zip",
        datetime_format="%Y%m%d",
        datetime_column="SETTLEMENTDATE",
        tables=['DISPATCH_UNIT_SOLUTION'])
}


def update_datasets(datasets, print_progress=False):
    """function that updates a subset of datasets (as a list) contained in DATASETS"""
    filehandler = CurrentFileHandler()
    print(datasets)
    for dataset_name in datasets:
        filehandler.update_data(DATASETS[dataset_name], print_progress=print_progress)
