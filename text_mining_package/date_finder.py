import datetime
import itertools
import re
import typing
from functools import lru_cache
from string import digits
from typing import Pattern

import numpy as np

from text_mining_package import NicDate, DateCaptureRegex


class DateFinderx:

    def __repr__(self):
        """
        :return: Date in american mm/dd/yyyy format (all numeric)
        """
        return f"{self.month}/{self.day}/{self.year}"

    def __init__(self, raw_text: str = ''):
        self.month = None
        self.day = None
        self.year = None

        cleaned_text = self.clean_text(raw_text=raw_text)
        regex_set = self.apply_regexes(search_text=cleaned_text)
        print("fin")

    def clean_text(self, raw_text: str = None):
        """
        The purpose of this function is to aid regex effectiveness by cleaning out character (period, comma, colon,
        semicolon) from the test string. Double spaces are also eliminated.

        :param raw_text: A string which will be used for date analysis.
        """
        clean_text = re.sub(pattern=r"[.,;:]", string=raw_text, repl='')
        cleaner_text = re.sub(pattern=r"\s{2,}", string=clean_text, repl=' ')
        return cleaner_text

    def apply_regexes(self, search_text: str = str()):
        """
        This function applies the regex patterns to the string, iterating until a match is found.
        :param search_text: String to search for a date with regexes It outputs a group dictionary
        :return: tuple of results
        """
        date_capture_regex = DateCaptureRegex.create_date_regex()
        for dcr in date_capture_regex:
            results = tuple(re.finditer(pattern=dcr, string=search_text))
            if len(results) == 0:
                continue
            if len(results) == 1:
                return results[0].groupdict()
            if len(results) > 1:
                print("selah")

        return None


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
