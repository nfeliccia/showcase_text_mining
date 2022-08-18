import datetime

import pytest

from text_mining_package import DateFinder

pydate_test_results = [("8/18/1972", (8, 18, 1972))]


@pytest.mark.parametrize("date_string, python_date", pydate_test_results)
def test_regex_validity(date_string, python_date):
    test_date_finder = DateFinder(raw_string=date_string)
    assert test_date_finder.year == python_date[2]
    assert test_date_finder.month == python_date[0]
    assert test_date_finder.day == python_date[1]
    assert test_date_finder.python_date == datetime.datetime(year=test_date_finder.year, month=test_date_finder.month,
                                                             day=test_date_finder.day)
