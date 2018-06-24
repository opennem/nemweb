"""Module for reading nemfiles and zipped nemfiles into pandas dataframes"""

from io import BytesIO
from zipfile import ZipFile
import pandas as pd

class ZipFileStreamer(ZipFile):
    """ZipFile subclass, with method to extract ZipFile as byte stream to memory"""

    def __init__(self, filename):
        """Initialises ZipFile object, and adds member_count attribute"""
        ZipFile.__init__(self, filename)
        self.member_count = len(self.filelist)

    def extract_stream(self, member):
        """Extract a member from the archive as a byte stream or string steam, using
        its full name. 'member' may be a filename or a ZipInfo object. """
        return BytesIO(self.read(member))

def zip_streams(fileobject):
    """Generator that yields each memeber of a zipfile as a BytesIO stream.
    Can take a filename or file-like object (BytesIO object) as an argument."""
    with ZipFileStreamer(fileobject) as zipfile:
        for filename in zipfile.namelist():
            yield filename, zipfile.extract_stream(filename)

def nemfile_reader(nemfile_object):
    """Returns a dict containing a pandas dataframe each table in a nemfile.
    The fileobject needs to be unzipped csv (nemfile), and can be either a file or an
    an in stream fileobject."""
    table_dict = {}
    for line in nemfile_object.readlines():
        rows = line.decode().split(',')
        table = "{0}_{1}".format(rows[1], rows[2])

        #new table
        if rows[0] == "I":
            table_dict[table] = line

        #append data to each table
        elif rows[0] == "D":
            table_dict[table] += line

    return {table:pd.read_csv(BytesIO(table_dict[table])) for table in table_dict}

def nemzip_reader(nemzip_object):
    """Returns a dict containing a pandas dataframe each table in a zipped nemfile.
    The fileobject is needs to be a zipped csv (nemzip), and can be either a file or an
    in stream fileobject.
    Function checks there is only one file to unzip, unzips to a nemfile (csv) in memory,
    and passes nemfile_object to nemfile reader."""
    with ZipFileStreamer(nemzip_object) as zipfile:
        if zipfile.member_count == 1:
            filename = zipfile.namelist()[0]
            nemfile_object = zipfile.extract_stream(filename)
            return nemfile_reader(nemfile_object)
        else:
            raise Exception('More than one file in zipfile')
