import datetime
import itertools
import re
import typing
from functools import lru_cache
from string import digits
from typing import Pattern

import numpy as np

from text_mining_package.nic_date_date_class import NicDate


class DateFinder:
    """
    Date Finder is the main class used to find a date in supported format in the line of text.
    :arg: str containing a date in the supported format
    """

    def __repr__(self):
        """
        :return: Date in american mm/dd/yyyy format (all numeric)
        """
        return f"{self.month}/{self.day}/{self.year}"

    def __init__(self, raw_string: str = str()):
        date_regexes_tuple = self.create_date_regex()
        nic_date_result = self.find_dates(date_regex_tuples=date_regexes_tuple, raw_string=raw_string)
        self.month = self.month_process_date(nic_date_result)
        self.day = self.day_process_date(nic_date_result)
        self.year = self.year_process_date(nic_date_result)
        self.python_date = self.convert_to_python_datetime()

    @lru_cache(maxsize=2)
    def find_dates(self, date_regex_tuples: tuple[Pattern[str], ...] = None, raw_string: str = str()) -> NicDate:
        """
        This function applies the regex to a given raw string to extract the dates results.
        :param date_regex_tuples: A list of compiled regex functions to test against the string.
        :param raw_string: A string in which to find a date pattern.
        :return: NicDate Object - with Month, Day and Year
        :rtype: NicDate
        """

        # This section pre-processes the string to make it more compatible with regex, removing anything that's not
        # a word character or a space
        raw_string = re.sub(r'^[^0-9a-zA-Z\\\-]', '', raw_string)

        # Since none of the dates are period delimited, we can remove periods and commas too.
        raw_string = re.sub(r'[\.,]', '', raw_string)

        ##########################################################################################################
        # List comprehension is used because it's the fastest way to iterate in Python
        # Loop through all regexes, perform a search, and find the hit by filtering out the Nones to get the match
        # object.Note I don't use an IF condition above because checking would require that the regex be run twice,
        # slowing things down.
        ###########################################################################################################
        search_results = [tuple(re.finditer(pattern=date_regex_tuple, string=raw_string)) for date_regex_tuple in
                          date_regex_tuples]
        search_results = list(itertools.chain.from_iterable([x for x in search_results if x]))

        if len(search_results) == 0:
            print(f"No date found in {raw_string}")
            raise ValueError
        # Dev code to check assumption that only one regex expression will match. Possible remove in production
        # for efficiency.

        # This is here because the regex patterns captured some junk as well as valid info. Example 'May 14,
        # 1989 QTc  467 ms  Pertinent Medical Review of Systems Constitutional: the QTc 476 Note the day default is
        # not None, but is one to fulfill the requirement September 1985 appear as September 1, 1985
        if len(search_results) > 1:

            # This is being added to handle the problem of multiple hits from regex.  First solution is to
            # assume the first match is best.
            search_results_collector = list()
            for search_result in search_results:
                # Generate the valid results.
                try:
                    dates_result = NicDate(month=search_result.groupdict().get('month', '1'),
                                           date=search_result.groupdict().get('day', '1'),
                                           year=search_result.groupdict().get('year', None))

                    self.month = self.month_process_date(dates_result)
                    self.day = self.day_process_date(dates_result)
                    self.year = self.year_process_date(dates_result)
                    search_results_collector.append(dates_result)
                except ValueError:
                    continue

            dates_result = search_results_collector.pop(0)

        elif len(search_results) == 1:
            search_result = search_results.pop()
            dates_result = NicDate(month=search_result.groupdict().get('month', '1'),
                                   date=search_result.groupdict().get('day', '1'),
                                   year=search_result.groupdict().get('year', None))

        return dates_result

    @lru_cache(maxsize=2)
    def create_date_regex(self) -> tuple[Pattern[str], ...]:
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
                               r'(?P<month>\w{3,})[,\s]+(?P<year>\d{4})', r'(?P<month>\d{1,2})[\/]+(?P<year>\d{4})',
                               r'\s\D(?P<year>\d{4})[\D\w\s]', r'\D+\s.(?P<year>\d{4})$',
                               r'(?:\D+\s)(?P<year>\d{4})(?:[\D\s]+)', r'^(?P<year>\d{4})(?:[\D\s+])',
                               r'(?:[\D+\s])(?P<year>\d{4})(?:[\D\s])')

        # This additional code was added in to handle the case of a 3 letter month with a stray typo e.g. pOct
        # IT may seem like overfitting, but at this point the best solution I could come up with was to regex the
        # months with an extra value before or after. Fortunately we have the month names (short & Long)  in the month
        # conversion dict.
        month_regex_strings = [fr'(?P<month_{month}>[\w\s]{month})[\w\s](?P<year>\d{4})' for month in
                               self.create_month_conversion_dict().keys()]
        regex_string_tuples = tuple(itertools.chain(*(regex_string_tuples, month_regex_strings)))

        # Note -Tuples use less memory. If mutation is not needed, tuples are used herein
        compiled_regex_tuple = tuple(
            [re.compile(pattern=regex_string_tuple, flags=re.IGNORECASE) for regex_string_tuple in regex_string_tuples])
        return compiled_regex_tuple

    @lru_cache(maxsize=2)
    def create_month_conversion_dict(self) -> dict:
        """
        The purpose of this function is to create a dictionary where keys are text which can represent a month, and the
        numbers are the sequence of the month from 1-12

        :return: dictionary where the keys are the short names of the month, and the values are the numerical sequence of the month.
        """

        ######################
        # Create Short Months
        ######################
        month_names_short = ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
        # Array is written as numbers 1-12 rather than generated because previous testing has shown direct read to be
        # faster
        month_numbers = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], dtype=np.uint8)
        month_conversion_dict = {a: b for a, b in zip(month_names_short, month_numbers)}

        ######################
        # Create Long Months
        ######################
        month_names_long = (
            'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
            'november', 'december', 'jan')
        month_conversion_dict.update({a: b for a, b in zip(month_names_long, month_numbers)})

        return month_conversion_dict

    @lru_cache(maxsize=2)
    def day_process_date(self, search_result: NicDate) -> np.uint8:
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
            this_month_max_date = NicDate.find_largest_day(result_month=self.month_process_date(search_result))
            if any((day_as_num < 0, day_as_num > this_month_max_date)):
                raise ValueError("Not a valid Date")
            return day_as_num
        else:
            raise ValueError("Non digit found in day")

    @lru_cache(maxsize=2)
    def month_process_date(self, search_result: NicDate) -> typing.Union[None, np.uint8]:
        """

        :param search_result: NicDate - DAte in Nicdate format
        :return: sequential number of the month.
        """
        month = search_result.month
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Handle the simple case where the month comes back as a digit. Validate that its between 1 and 12.
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if month is None:
            return np.uint8(1)

        if month.isdigit():
            month_as_num = np.uint8(month)
            if any((month_as_num < 0, month_as_num > 12)):
                raise ValueError(f"Bad Month info {month_as_num}")
            return month_as_num
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Since we allow typos in to the month, we have to handle them here. The first case handles a proper month
        # which is not a typo. IF there is a typo we search all the months (which are the keys of the month convers
        # ion dictionary.
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        elif month.isalpha():
            mcd = self.create_month_conversion_dict()
            mcd_keys = tuple(mcd.keys())
            # The nice simple case.
            if month in mcd_keys:
                month_as_num = mcd.get(month.lower(), np.nan)
            # The complicated Case.
            else:
                month_searcher_regex_string = "|".join([fr"{clean_month}" for clean_month in mcd_keys])
                month_search_regex = re.compile(month_searcher_regex_string, re.IGNORECASE)
                month_search_result = re.search(pattern=month_search_regex, string=month)
                if month_search_result is None:
                    month_as_num = np.nan
                else:
                    clean_month = month_search_result.group(0)
                    month_as_num = mcd.get(clean_month.lower(), np.nan)
            # Handle the case where the dictionary doesn't work.
            if month_as_num is np.nan:
                month_as_num = np.uint8(1)
            return month_as_num
        elif month.isalnum():
            search_result.month = search_result.month.strip(digits)
            new_search_result_month = self.month_process_date(search_result=search_result)
            return new_search_result_month

    def year_process_date(self, nic_date_result: NicDate) -> np.uint16:
        """
        The purpose of this function is to process the year in a NicDate object.
        Two digit years are assumed to be the 20th century (19XX). Four digit years are passed through. Anything other
        than a two or four digit year will fail.

        :param nic_date_result: NicDate object from which to extract the year
        :type nic_date_result: NicDate
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

    def convert_to_python_datetime(self):
        python_date_time = datetime.datetime(year=self.year, month=self.month, day=self.day)
        return python_date_time
