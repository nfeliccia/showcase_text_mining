import copy
import re
from pathlib import Path

import pandas as pd

from text_mining_package.date_finder import DateFinderx

cumulative_match_series = pd.Series(data=None, name='match_objects', dtype=object)

dates_series = pd.Series(
    data=Path(r"F:\coursera_python_text_mining\dates.txt").read_text(encoding='utf-8').splitlines(),
    name='target_phrases')
original_date_series = copy.copy(dates_series)

extraction_series_a = original_date_series.apply(lambda x: DateFinderx(raw_text=x))

for regex_aaa in regex_comber_series:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Pre clean text - remove periods and commas, and double spaces
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    dates_series = dates_series.apply(lambda x: re.sub(pattern=r"[.,:]", string=x, repl='')).apply(
        lambda x: re.sub(pattern=r"\s{2,}", string=x, repl=' '))

    #####################################################
    # Apply the regex formula to the existing date series.
    #####################################################
    series_aaa = dates_series.apply(lambda x: tuple(re.finditer(pattern=regex_aaa, string=x)))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Make a Filter Series and make a series of which ones to keep.
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    series_aaa_keepers = series_aaa.loc[series_aaa.astype(bool)].copy(deep=True)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # remove the keepers from the big data series
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    dates_series = dates_series.drop(index=series_aaa_keepers.index)
    cumulative_match_series = pd.concat((cumulative_match_series, series_aaa_keepers))

dates_series_text = "\n".join(dates_series.to_list())
Path(fr"C:\temp\dates_aaa_x.txt").write_text(data=dates_series_text, encoding='utf-8')

cumulative_match_series = cumulative_match_series.sort_index()
match_series_length = cumulative_match_series.apply(lambda x: len(x))
hit_re = cumulative_match_series.apply(lambda x: x[0].re)
match_re = cumulative_match_series.apply(lambda x: x[0].group(0))
full_res_df = pd.concat((original_date_series, cumulative_match_series, match_series_length, hit_re, match_re), axis=1)

full_res_path = Path(r"C:\temp\full_res_df.xlsx")
full_res_df_writer = pd.ExcelWriter(path=full_res_path, engine='openpyxl')

with full_res_df_writer:
    full_res_df.to_excel(excel_writer=full_res_df_writer, index=False)
print("fin")
