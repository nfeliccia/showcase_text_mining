import copy
from pathlib import Path

import pandas as pd

from text_mining_package.date_finder import DateFinderx

cumulative_match_series = pd.Series(data=None, name='match_objects', dtype=object)

dates_series = pd.Series(
    data=Path(r"F:\coursera_python_text_mining\dates.txt").read_text(encoding='utf-8').splitlines(),
    name='target_phrases')
original_date_series = copy.copy(dates_series)
extraction_series_a = pd.Series(data=original_date_series.apply(lambda x: DateFinderx(raw_text=x).pydate))
series_as_pandas_dt = pd.to_datetime(extraction_series_a).dt.date.sort_values().index.to_series().reset_index(drop=True)
print("Fin")
