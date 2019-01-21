import pytest
import pytz

from nemweb.utils import local_to_nem_tz, utc_to_nem
from datetime import datetime as dt


@pytest.mark.parametrize(
    'utc, expected',
    (
        #  simple 10 hours ahead
        (dt(2019, 1, 21, 0, 0, 0), dt(2019, 1, 21, 10, 0, 0, 0)),
        #  covering two days
        (dt(2025, 12, 4, 23, 0, 0), dt(2025, 12, 5, 9, 0, 0)),
    )
)
def test_utc_to_nem(utc, expected):
    assert expected == utc_to_nem(utc)

#  TODO same test for local_to_nem_tz
