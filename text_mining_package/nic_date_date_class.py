import re
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
    def month_names_short() -> tuple:
        mns = ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
        return mns

    @lru_cache(maxsize=2)
    @staticmethod
    def month_names_long() -> tuple:
        mnl = (
        'january', 'february', 'march', 'april', 'May', 'june', 'july', 'august', 'september', 'october', 'november',
        'december',)
        return mnl

    def verify_not_none(self):
        """
        This function returns an error when called if any of the components are none.

        :raises ValueError if any of the components are None.
        """
        if any((self.month is None, self.date is None, self.year is None)):
            raise ValueError("None Value passed")

    @staticmethod
    @lru_cache(maxsize=12)
    def month_conversion_dict() -> dict:
        """
        The purpose of this function is to create a dictionary where keys are text which can represent a month, and the
        numbers are the sequence of the month from 1-12

        :return: dictionary where the keys are the short names of the month, and the values are the numerical sequence of the month.
        """
        # Array is written as numbers 1-12 rather than generated because previous testing has shown direct read to be
        # faster
        month_numbers = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
        month_conversion_dict = {a: b for a, b in zip(NicDate.month_names_short(), month_numbers)}
        month_conversion_dict.update({a: b for a, b in zip(NicDate.month_names_long(), month_numbers)})
        return month_conversion_dict

    @staticmethod
    def find_largest_day(result_month: int = 0) -> dict:
        """
        The purpose of this function is to determine the largest day in the month. It supports date validation utilities
        At some point I'd like to add leap year functionality to it
        TODO: Add leap year functionality someday.
        :param result_month: integer
        :return: integer
        """
        largest_day_dict = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
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
        # Note- Any is used here to speed up analysis with switching.
        if not any((0 < year < 100, 1900 < year < 2030)):
            valid_year = False
        return valid_year

    def is_valid_month(self, month: typing.Union[int, str] = None):
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # None is an acceptable value for month.
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if month is None:
            return True

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Handle the case where digits are passed either directly or as a non string
        #  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
            month = self.month_conversion_dict().get(month, None)
        else:
            month = int(month)
        day = np.uint8(day)
        is_valid_day = 0 < day < self.find_largest_day(result_month=month)
        return is_valid_day

    def valid_date(self, in_match_result: re.Match):
        """
        The purpose of this function is to determine the validity of a match object returned from regex.
        It returns a score from 0 to 8 with 8 being the most likely valid date, and 0 being not a valid date, and 8
        being the most likely date.
        :param in_match_result: A dictionary generated by group date of regex.
        :return: integer from 0-8
        :rtype np.uint8:
        """

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # First test the year. If the year isn't valid then forget about it
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        in_match_result = in_match_result.groupdict()

        year_result = self.is_valid_year(year=in_match_result.get('year', None))
        if not year_result:
            return np.uint8(0)
        else:
            validity_score = 1

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Test the month. a Null Month is OK, else bump validity score to 4
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        month_result = self.is_valid_month(month=in_match_result.get('month', None))
        if not month_result:
            return validity_score
        else:
            validity_score += 3

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Test the day.
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        day_result = self.is_valid_day(month=in_match_result.get('month', None), day=in_match_result.get('day', None))
        if day_result:
            validity_score += 4
        return validity_score
