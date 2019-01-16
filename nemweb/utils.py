import pickle
import pytz
import datetime


def dump_pickle(obj, name):
    """
    Saves an object to a pickle file.

    args
        obj (object)
        name (str) path of the dumped file
    """
    with open(name, 'wb') as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(name):
    """
    Loads a an object from a pickle file.

    args
        name (str) path to file to be loaded

    returns
        obj (object)
    """
    with open(name, 'rb') as handle:
        return pickle.load(handle)



def utc_to_nem_tz(dt):
    """Convert between naive utc and naive NEM time"""

    #convert naive utc to tz aware datetime
    dt_utc = pytz.UTC.localize(dt)

    #convert to new tz (NEM tz
    nem_tz = pytz.FixedOffset(600)
    dt_nem = dt_utc.astimezone(nem_tz)

    #return new timezone (naive)
    return dt_nem.replace(tzinfo=None)
