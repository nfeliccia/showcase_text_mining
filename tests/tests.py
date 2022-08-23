import datetime

import pytest

from text_mining_package import DateFinder, NicDate

pydate_test_results = [("20 Mar 2009", (3, 20, 2009)), ("03/25/93 Total time of visit (in minutes):", (3, 25, 1993)),
                       ("6/18/85 Primary Care Doctor", (6, 18, 1985)),
                       ("she plans to move as of 7/8/71 In-Home Services: None", (7, 8, 1971)),
                       ("(4/10/71)Score-1Audit C Score Current:", (4, 10, 1971)),
                       ("4-13-82 Other Child Mental Health Outcomes Scales Used", (4, 13, 1982)),
                       ("September 06, 1995 Total time of visit (in minutes):", (9, 6, 1995)), (
                           "r August 12 2004 - diagnosed with Parkinson's stopped working Financial Stress: No",
                           (8, 12, 2004)), ("04/20/2009", (4, 20, 2009)), ("04/20/99", (4, 20, 1999)),
                       ("4/20/99", (4, 20, 1999)), ("4/3/99", (4, 3, 1999)), ("Mar 21st, 2009", (3, 21, 2009)),
                       ("Mar 22nd, 2009", (3, 22, 2009)), ]

"""
 
 
Feb 2009; Sep 2009; Oct 2010
6/2008; 12/2009
2009; 2010
"""


@pytest.mark.parametrize("date_string, python_date", pydate_test_results)
def test_regex_validity(date_string, python_date):
    test_date_finder = DateFinder(raw_string=date_string)
    assert test_date_finder.year == python_date[2]
    assert test_date_finder.month == python_date[0]
    assert test_date_finder.day == python_date[1]
    assert test_date_finder.python_date == datetime.datetime(year=test_date_finder.year, month=test_date_finder.month,
                                                             day=test_date_finder.day)


def test_get_month_nome(month_seed):
    month_num = int(NicDate.month_conversion_dict().get(month_seed.lower(), None))
    return month_num
