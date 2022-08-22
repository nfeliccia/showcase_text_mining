import datetime
import re

from text_mining_package import NicDate, DateCaptureRegex


class DateFinderx:
    """
    The purpose of this class is to find dates in text strings.
    :param raw_text: Raw text from which a date is to be extracted.
    :
    """

    def __repr__(self):
        """
        :return: Date in american mm/dd/yyyy format (all numeric)
        """
        return f"{self.month}/{self.day}/{self.year}"

    def __init__(self, raw_text: str = ''):
        """


        """
        self.month = None
        self.day = None
        self.year = None

        cleaned_text = self.clean_text(raw_text=raw_text)
        result_dict = self.apply_regexes(search_text=cleaned_text)
        self.pydate = self.create_pydate(result_dict=result_dict)

    def clean_text(self, raw_text: str = None) -> str:
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
        :return: dictionary of month, day and year
        """
        date_capture_regex = DateCaptureRegex.create_date_regex()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Iterate through the regexes. Have three cases, first, no match, just continue iterating
        # second case, one result, grab the group dictionary of the first.
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for dcr in date_capture_regex:
            results = tuple(re.finditer(pattern=dcr, string=search_text))
            if len(results) == 0:
                continue
            if len(results) == 1:
                return results[0].groupdict()
            if len(results) > 1:
                validity_results = [(result, NicDate().valid_date(in_match_result=result)) for result in results]
                validity_results = sorted(validity_results, key=lambda x: x[1], reverse=True)
                best_result = validity_results[0][0].groupdict()
                return best_result

    def create_pydate(self, result_dict: dict = None):
        try:
            year_seed = int(result_dict.get('year'))
            if year_seed < 100:
                year_seed = year_seed + 1900
            self.year = year_seed
        except TypeError as uhoh:
            print(f"{uhoh}")

        month_seed = result_dict.get('month', 1)
        if isinstance(month_seed, str) and month_seed.isalpha():
            try:
                month_num = int(NicDate.month_conversion_dict().get(month_seed.lower(), None))
            except TypeError as uhoh:
                print(f"{uhoh}")
        else:
            month_num = int(month_seed)
            if not 0 < month_num < 13:
                raise ValueError
        self.month = month_num
        self.day = int(result_dict.get('day', 1))
        try:
            return datetime.date(year=self.year, month=self.month, day=self.day)
        except ValueError as uhoh:
            print(f"{uhoh}")
