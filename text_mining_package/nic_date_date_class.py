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

    def verify_not_none(self):
        """
        This function returns an error when called if any of the components are none.

        :raises ValueError if any of the components are None.
        """
        if any((self.month is None, self.date is None, self.year is None)):
            raise ValueError("None Value passed")

    @staticmethod
    @lru_cache(maxsize=12)
    def find_largest_day(result_month: int = 0) -> dict:
        months_numerical = np.arange(start=1, stop=13).astype(np.uint8)
        month_max_days = np.array((31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)).astype(np.uint8)
        largest_day_dict = {a: b for a, b in zip(months_numerical, month_max_days)}
        largest_day = largest_day_dict.get(result_month, np.nan)
        return largest_day
