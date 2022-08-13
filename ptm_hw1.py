import re
import typing
from dataclasses import dataclass
from functools import lru_cache
from typing import Pattern

import numpy as np
import pandas as pd


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


@lru_cache(maxsize=2)
def create_date_regex() -> tuple[Pattern[str], ...]:
    """
    This function creates a complex regex pattern by concatenating strings and then compiling.
    It is wrapped in a @lru_cache so the code only has to be run once per instance.
    Named groups are used to set up dictionaries in groupdict() so results can be addressed by a common structure.

    :return: re.Pattern - regex pattern to find dates.
    """
    # Keeping the compilation in a separate function helps keep code clean and readable
    # In order to use repeated names we have to compile each separately.
    regex_string_tuples = (r'(?P<mmddyyyy>(?P<month>\d{1,2})[\-/](?P<day>\d{1,2})[\-/](?P<year>\d{1,4}))',
                           r'(?P<ddmmmyyyy>(?P<day>\d{1,2})\s+(?P<month>\w{3,})\s+(?P<year>[\d{2}|\d{4}]\s))',
                           r'(?P<ddmmmyy>(?P<month>\w{3,})\s+(?P<day>\d{1,2})[,\s]+(?P<year>\d{2}\s))',
                           r'(?P<ddmmmyyyy>(?P<month>\w{3,})\s+(?P<day>\d{1,2})[,\s]+(?P<year>\d{4}))',
                           r'(?P<month>\w{3,})[,\s]+(?P<year>\d{4})')

    # Note -Tuples use less memory. If mutation is not needed, tuples are used herein
    compiled_regex_tuple = tuple(
        [re.compile(pattern=regex_string_tuple, flags=re.IGNORECASE) for regex_string_tuple in regex_string_tuples])
    return compiled_regex_tuple


@lru_cache(maxsize=2)
def create_month_conversion_dict() -> dict:
    """
    The purpose of this function is to create a dictionary where keys are text which can represent a month, and the
    numbers are the sequence of the month from 1-12

    :return: dictionary where the keys are the short names of the month, and the values are the numerical sequence of the month.
    """

    ######################
    # Create Short Months
    ######################
    month_names_short = ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
    # Array is written as numbers 1-12 rather than generated because previous testing has shown direct read to be faster
    month_numbers = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], dtype=np.uint8)
    month_conversion_dict = {a: b for a, b in zip(month_names_short, month_numbers)}

    ######################
    # Create Long Months
    ######################
    month_names_short = (
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
        'december', 'jan')
    month_conversion_dict.update({a: b for a, b in zip(month_names_short, month_numbers)})

    return month_conversion_dict


@lru_cache(maxsize=2)
def day_process_date(search_result: NicDate) -> np.uint8:
    """
    The purpose of this function is to process the date part of the NicDate object. It verifies that it's a valid date.
    Validation includes greater than 0, and less than 29, 30, or 31 depending on the Month.

    :param search_result: Object of NicDate type from which to process the date.
    :return: The day number of the month, validated to make sure it's a valid date. (e.g.) No Feb 31st, June 33rd.
    """

    # None is an acceptable value because the requirements state that September 1, 1985 should be handled as 1
    # set value to string of one and handle normally
    if search_result.date is None:
        return np.uint8(1)

    if search_result.date.isdigit():
        day_as_num = np.uint8(search_result.date)
        this_month_max_date = NicDate.find_largest_day(result_month=month_process_date(search_result))
        if any((day_as_num < 0, day_as_num > this_month_max_date)):
            raise ValueError("Not a valid Date")
        return day_as_num
    else:
        raise ValueError("Non digit found in day")


@lru_cache(maxsize=2)
def month_process_date(search_result: NicDate) -> typing.Union[None, np.uint8]:
    """

    :param search_result: NicDate - DAte in Nicdate format
    :return: sequential number of the month.
    """
    month = search_result.month
    if month.isdigit():
        month_as_num = np.uint8(month)
        if any((month_as_num < 0, month_as_num > 12)):
            raise ValueError(f"Bad Month info {month_as_num}")
        return month_as_num
    elif month.isalpha():
        month_as_num = create_month_conversion_dict().get(month.lower(), np.nan)
        if month_as_num is np.nan:
            raise ValueError(f"Month letters not found")
        return month_as_num
    elif month.isalnum():
        raise ValueError("Mixed Data Found")


def year_process_date(nic_date_result: NicDate) -> np.uint16:
    """
    The purpose of this function is to process the year in a NicDate object.
    Two digit years are assumed to be the 20th century (19XX). Four digit years are passed through. Anything other
    than a two or four digit year will fail.

    :param nic_date_result: NicDate object from which to extract the year
    :return: YYYY four digit representation of the year.
    """

    #####################################################
    # Handle 2 year case with assumption of 20th century
    #####################################################
    if len(nic_date_result.year) == 2:
        year_number = np.uint16(f"19{nic_date_result.year}")
    elif len(nic_date_result.year) == 4:
        year_number = np.uint16(nic_date_result.year)
    else:
        raise ValueError("Incorrect Year Parsed")

    return year_number


@lru_cache(maxsize=2)
def find_dates(date_regex_tuples: tuple[Pattern[str], ...] = None, raw_string: str = str()) -> NicDate:
    """
    This function applies the regex to a given raw string to extract the dates results.
    :param date_regex_tuples: A list of compiled regex functions to test against the string.
    :param raw_string: A string in which to find a date pattern.
    :return: NicDate Object - with Month, Day and Year
    """

    # This section pre-processes the string to make it more compatible with regex, removing anything that's not
    # a word character or a space

    raw_string = re.sub(r'\.', '', raw_string)
    ##########################################################################################################
    # List comprehension is used because it's the fastest way to iterate in Python
    # Loop through all regexes, perform a search, and find the hit by filtering out the Nones to get the match
    # object.Note I don't use an IF condition above because checking would require that the regex be run twice,
    # slowing things down.
    ###########################################################################################################
    search_results = [re.search(pattern=date_regex_tuple, string=raw_string) for date_regex_tuple in date_regex_tuples]
    search_results = [search_result for search_result in search_results if search_result]

    if len(search_results) == 0:
        print(f"No date found in {raw_string}")
        raise ValueError
    # Dev code to check assumption that only one regex expression will match. Possible remove in production
    # for efficiency.

    # This is here because the regex patterns captured some junk as well as valid info.
    # Example 'May 14, 1989 QTc  467 ms  Pertinent Medical Review of Systems Constitutional:
    # the QTc 476
    # Note the day default is not None, but is one to fulfill the requirement September 1985 appear as September 1, 1985
    if len(search_results) > 1:
        for search_result in search_results:
            try:
                dates_result = NicDate(month=search_result.groupdict().get('month', None),
                                       date=search_result.groupdict().get('day', None),
                                       year=search_result.groupdict().get('year', None))
                dates_result.verify_not_none()
                fd_month = month_process_date(dates_result)
                fd_day = day_process_date(dates_result)
                fk_year = year_process_date(dates_result)
                print(f"{fd_month=}\t{fd_day=}\t{fk_year}")
                search_results = [dates_result, ]

            except ValueError:
                continue

    elif len(search_results) == 1:
        search_result = search_results.pop()

        dates_result = NicDate(month=search_result.groupdict().get('month', None),
                               date=search_result.groupdict().get('day', None),
                               year=search_result.groupdict().get('year', None))

    return dates_result


class DateFinder:
    """
    Date Finder is the main class used to find a date in supported format in the line of text.
    :arg: str containing a date in the supported format.
    """

    def __repr__(self):
        """
        :return: Date in american mm/dd/yyyy format.
        """
        return f"{self.month}/{self.day}/{self.year}"

    def __init__(self, raw_string: str = str()):
        date_regexes_tuple = create_date_regex()
        nic_date_result = find_dates(date_regex_tuples=date_regexes_tuple, raw_string=raw_string)
        self.month = month_process_date(nic_date_result)
        self.day = day_process_date(nic_date_result)
        self.year = year_process_date(nic_date_result)


if __name__ == "__main__":

    doc = []
    with open(r'.\dates.txt') as file:
        for line in file:
            doc.append(line)

    medical_dates_df = pd.Series(doc)

    error_counter = 0
    for x in range(0, 500):
        text_to_process = doc[x]
        try:
            found_date = DateFinder(raw_string=text_to_process)
        except ValueError as uhoh:
            print(f"count={x}\t{doc[x]}")
            error_counter += 1

    print(f"{error_counter=}")
    print("fin")
