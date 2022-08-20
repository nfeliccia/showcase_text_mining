import typing
from dataclasses import dataclass
from functools import lru_cache

import numpy as np


@dataclass
class NicDate(dict):
    """
    The NicDate Class inputs the string values from regex search for month, day and year.
    It inherits from dictionary.
    A dataclass is used instead of a raw dictionary, because a dictionary is not hashable, and can not be cached by
    @lru_cache. This class is  hashable and able to be reused in @lru_cache functions.

    :raises: Value Error if verify_not_none method is called and
    """

    def __hash__(self):
        # Define a specific has for this class, so it can be cached.
        hash_seed = hash(f"{self.month}/{self.date}/{self.year}")
        return hash_seed

    def __init__(self, month: str = str(), date: str = str(), year: str = ()):
        super().__init__()
        self.month = month
        self.date = date
        self.year = year

    def __repr__(self):
        return f"Day = {self.date} Month = {self.month} Year = {self.year}"

    @lru_cache(maxsize=2)
    @staticmethod
    def month_names_short():
        mns = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        return mns

    @lru_cache(maxsize=2)
    @staticmethod
    def month_names_long():
        mnl = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
               'november', 'december', ]
        return mnl

    def verify_not_none(self):
        """
        This function returns an error when called if any of the components are none.

        :raises ValueError if any of the components are None.
        """
        if any((self.month is None, self.date is None, self.year is None)):
            raise ValueError("None Value passed")

    @lru_cache(maxsize=12)
    def month_conversion_dict(self) -> dict:
        """
        The purpose of this function is to create a dictionary where keys are text which can represent a month, and the
        numbers are the sequence of the month from 1-12

        :return: dictionary where the keys are the short names of the month, and the values are the numerical sequence of the month.
        """
        # Array is written as numbers 1-12 rather than generated because previous testing has shown direct read to be
        # faster
        month_numbers = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], dtype=np.uint8)
        month_conversion_dict = {a: b for a, b in zip(self.month_names_short, month_numbers)}
        month_conversion_dict.update({a: b for a, b in zip(self.month_names_long, month_numbers)})
        return month_conversion_dict

    @staticmethod
    @lru_cache(maxsize=12)
    def find_largest_day(result_month: int = 0) -> dict:
        months_numerical = np.arange(start=1, stop=13).astype(np.uint8)
        month_max_days = np.array((31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)).astype(np.uint8)
        largest_day_dict = {a: b for a, b in zip(months_numerical, month_max_days)}
        largest_day = largest_day_dict.get(result_month, np.nan)
        return largest_day

    def is_valid_year(self, year: typing.Union[int, str] = None) -> bool:
        """
        The purpose of this function is to determine whether a year (either int or string) is a valid year.
        Accommodates two digits and four digit values.

        :param year: Either string or integer representing year
        :return: bool True if  year is valid.
        """
        valid_year = True
        # ~~~~~~~~~~~~~~~~~~~
        # Test the year first
        # ~~~~~~~~~~~~~~~~~~~
        if year is None:
            valid_year = False
            return valid_year

        # ~~~~~~~~~~~~~~~~~~~
        # Accommodate Strings
        # ~~~~~~~~~~~~~~~~~~~
        if not isinstance(year, int):
            year = int(year)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Check between 0 and 100 for two digit range (pretty much any two digit)
        # Check between 1900 and 2030 for a valid year digit.
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        two_digit_ok = 0 < year < 100
        four_digit_ok = 1900 < year < 2030
        if not two_digit_ok or not four_digit_ok:
            valid_year = False
        return valid_year

    def is_valid_month(self, month: typing.Union[int, str] = None):
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # None is an acceptable value for month.
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if month is None:
            return True

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Handle the case where digits are passed either directly or as a non string
        #  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if (isinstance(month, str) and month.isdigit()) or isinstance(month, int):
            valid_month = 0 < int(month) < 13
            return valid_month

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Handle the name case where a name is passed.
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        elif isinstance(month, str):
            valid_month = any((month.lower() in self.month_names_short, month.lower() in self.month_names_long))
            return valid_month

    def is_valid_day(self, month: typing.Union[int, str] = None, day: typing.Union[int, str] = None):

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # If there's no month, then the day doesn't matter, so its ok
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if month is None:
            return True

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # By clearing non valid months here, we eliminate having to put a lot of error checking in the code below.
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if not self.is_valid_month(month):
            return False

        if month.isalpha():
            month = self.month_conversion_dict.get(month, None)
        else:
            month = np.uint8(month)
        day = np.uint8(day)
        is_valid_day = 0 < day < self.find_largest_day(result_month=month)
        return is_valid_day
