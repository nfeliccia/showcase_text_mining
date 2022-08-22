import itertools
import random
import re
from functools import lru_cache

from text_mining_package import NicDate


class DateCaptureRegex:
    """
    This is a wrapper class for the create_date_regex function.
    It has been separated into a class for future scalability of regex.
    """

    def __init__(self):
        pass

    def __hash__(self):
        """
        Hash required for using lru_cache.
        :return: int
        """

        return random.getrandbits(63)

    @lru_cache(maxsize=2)
    @staticmethod
    def create_date_regex() -> tuple:
        """
        This function creates a tuple of regex patterns to be used in searching for date.
        :return: re.Pattern - regex pattern to find dates.
        """

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create list of month names for iteration
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        months = itertools.chain(NicDate.month_names_short(), NicDate.month_names_long())

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create the initial regex strings which will catch numeric instances of dates and 3 letter months
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        regex_builder = [r"(?P<a>(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4}))",
                         r"(?P<b>(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{2}))",
                         r"(?P<c>(?P<month>\d{1,2})\-(?P<day>\d{1,2})\-(?P<year>\d{4}))",
                         r"(?P<d>(?P<month>\d{1,2})\-(?P<day>\d{1,2})\-(?P<year>\d{2}))",
                         r"(?P<e>(?P<day>\d{1,2})\s+(?P<month>[a-zA-Z]{3})\s+(?P<year>\d{4}))"]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Build strings with different patterns, but for each month
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        regex_builder.extend([fr"(?P<f>(?P<day>\d\d)\s+(?P<month>{x})\s+(?P<year>\d\d\d\d))" for x in months])
        regex_builder.extend([fr"(?P<g>(?P<day>\d)\s+(?P<month>{x})\s+(?P<year>\d\d\d\d))" for x in months])
        regex_builder.extend([fr"(?P<h>(?P<day>\d)\s+(?P<month>{x})\s+(?P<year>\d\d))" for x in months])
        regex_builder.extend([fr"(?P<i>(?P<day>\d\d)\s+(?P<month>{x})\s+(?P<year>\d\d))" for x in months])
        regex_builder.extend([fr"(?P<j>(?P<month>{x})\s+(?P<day>\d\d)\s+(?P<year>\d\d\d\d))" for x in months])
        regex_builder.extend([fr"(?P<k>(?P<month>{x})\s+(?P<day>\d)\s+(?P<year>\d\d\d\d))" for x in months])
        regex_builder.extend([fr"(?P<m>(?P<month>{x})\s+(?P<day>\d\d)\s+(?P<year>\d\d))" for x in months])
        regex_builder.extend([fr"(?P<l>(?P<month>{x})\s+(?P<day>\d)\s+(?P<year>\d\d))" for x in months])
        regex_builder.extend([fr"(?P<o>(?P<month>{x})\s+(?P<year>\d\d\d\d))" for x in months])
        regex_builder.extend([fr"(?P<n>(?P<month>{x})\s+(?P<year>\d\d))" for x in months])
        regex_builder.append(r"(?P<p>(?P<month>\d{1,2})[\s+/](?P<year>\d{4}))")
        regex_builder.append(r"(?P<q>(?P<month>\d{1,2})[\s+/](?P<year>\d{2}))")
        regex_builder.extend([fr"(?P<year>{x})" for x in range(1900, 2050)])
        regex_tuple = tuple([re.compile(pattern=regex_build, flags=re.IGNORECASE) for regex_build in regex_builder])
        return regex_tuple
