"""Module for downloading data different 'CURRENT' nemweb dataset
(selected data sets from files from http://www.nemweb.com.au/Reports/CURRENT)

Module includes one main superclass for handling generic nemweb current files. A series of
namedtuples (strored in global constant DATASETS) contains the relevant data for specfic datasets.
Datasets included from 'CURRENT' index page:

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
import numpy as np
from nemweb import nemfile_reader, nemweb_sqlite


class CurrentFileHandler:
    """class for handling 'WA' nemweb files from http://data.wa.aemo.com.au
    Requires a 'WADataset' namedtuple with following fields:

    - nemweb_name: the name of the dataset to be download (e.g. Dispatch_SCADA)
    - filename_pattern: a regex expression to match and a determine datetime from filename
      on nemweb. As example, for files in the Facility_SCADA dataset
      (e.g "facility-scada-2019-01.csv") the regex
      file_patten is facility-scada-([0-9]{4}-[0-9]{2}).csv
    - the format of the string to strip the datetime from. From the above example, the
      match returns '2019-01', so the string is "%Y-%m",
    - the list of tables to insert from each dataset e.g FACILITY_SCADA.
    """

    def __init__(self):
        self.base_url = "http://data.wa.aemo.com.au"
        self.section = "public/public-data/datafiles"

    def update_data(
            self,
            dataset,
            print_progress=False,
            db_name='nemweb_wa.db',
            start_date=None
    ):
        """Main method to process nemweb dataset
        - downloads the index page for the dataset
        - determines date to start downloading from
        - matches the start date against files in the index
        - inserts new files into database"""
        if start_date is None:
            start_date = nemweb_sqlite.start_from(
                table_name=dataset.tables[0],
                timestamp_col=dataset.datetime_column,
                db_name=db_name
            )
        print("Updating " + dataset.dataset_name)
        page = requests.get("{0}/{1}/{2}/".format(self.base_url,
                                                  self.section,
                                                  dataset.dataset_name))
        regex = re.compile("/{0}/{1}/{2}".format(self.section,
                                                 dataset.dataset_name,
                                                 dataset.nemfile_pattern))

        for match in regex.finditer(page.text):
            file_datetime = datetime.datetime.strptime(match.group(1), dataset.datetime_format)
            if file_datetime > start_date:
                nemfile = self.download(match.group(0), dataset.tables[0])
                if print_progress:
                    print(dataset.dataset_name, file_datetime)
                for table in dataset.tables:
                    dataframe = nemfile[table].drop_duplicates().copy()
                    nemweb_sqlite.insert(dataframe, table, db_name)
            else:
                print("%s before %s, Skipping" % (start_date, file_datetime))

    def download(self, link, table=None):
        """Dowloads nemweb zipfile from link into memory as a byteIO object.
        nemfile object is returned from the byteIO object """
        response = requests.get("{0}{1}".format(self.base_url, link))
        csv_strings = BytesIO(response.content)
        nemfile = nemfile_reader.nemfile_reader(csv_strings, table, DTYPES)
        return nemfile


#  class factory function for containing data for 'WA' datasets
WADataset = namedtuple("NemwebWAFile",
                            ["dataset_name",
                             "nemfile_pattern",
                             "datetime_format",
                             "datetime_column",
                             "tables"])

DATASETS = {
    "facility_scada": WADataset(
        dataset_name="facility-scada",
        nemfile_pattern="facility-scada-([0-9]{4}-[0-9]{2}).csv",
        datetime_format="%Y-%m",
        datetime_column="Trading Interval",
        tables=['FACILITY_SCADA']),

    "balancing_summary": WADataset(
        dataset_name="balancing-summary",
        nemfile_pattern="balancing-summary-([0-9]{4}).csv",
        datetime_format="%Y",
        datetime_column="Trading Interval",
        tables=['BALANCING_SUMMARY']),

    "load_summary": WADataset(
        dataset_name="load-summary",
        nemfile_pattern="load-summary-([0-9]{4}).csv",
        datetime_format="%Y",
        datetime_column="Trading Interval",
        tables=['LOAD_SUMMARY'])
}

""" defince datatype for table columns. Speeds up parsing and means that pandas doesn't
choke on large csv files. # Details from data.wa.aemo.com.au. TODO: Keeping dates as
strings for now"""
DTYPES = {
    # facility scada
    "Trading Date": str, # YYYY-MM-DD TODO:dataetime64 ?
    "Interval Number": np.uint8, # 1..48
    "Trading Interval": str, # YYYY-MM-DD HH:MM:SS TODO:datetime64 ?
    "Participant Code": str, # String
    "Facility Code": str, # String
    "Energy Generated (MWh)": float, # MWh
    "EOI Quantity (MW)": float, # MW
    "Extracted At": str, # YYYY-MM-DD HH:MM:SS TODO:datetime64 ?
    # balacing summary
    "Load Forecast (MW)": float, # MW
    "Forcast As At": str, # YYYY-MM-DD HH:MM:SS TODO:datetime64 ?
    "Scheduled Generation (MW)": float, # MW
    "Non-Scheduled Generation (MW)": float, #MW
    "Total Generation (MW)": float, # MW
    "Final Price ($/MWh)": float, # $/MWh
    # load summary
    "Resource Plan Generation (excluding Verve; MWh)": float, # MWh
    "Scheduled Generation (excluding Verve; MWh)": float, #MWh
    "Non-Scheduled Generation (excluding Verve; MWh)": float, # MWh
    "Scheduled Generation (Verve; MWh)": float, # MWh
    "Non-Scheduled Generation (Verve; MWh)": float, # MWh
    "Metered Generation (Total; MWh)": float, # MWh
    "Operational Load (MWh)": float, # MWh
    "Estimated Load Curtailment (MW)": float # MW
}

def update_datasets(datasets, print_progress=False):
    """function that updates a subset of datasets (as a list) contained in DATASETS"""
    filehandler = CurrentFileHandler()
    for dataset_name in datasets:
        filehandler.update_data(DATASETS[dataset_name], print_progress=print_progress)
