import timeit
from functools import lru_cache

import numpy as np

from ptm_hw1 import create_largest_day_dict


@lru_cache(maxsize=1)
def manual_dict():
    return {1: np.uint8(31), 2: np.uint8(23), 3: np.uint8(31), 4: np.uint8(30), 5: np.uint8(31), 6: np.uint8(30),
            7: np.uint8(31), 8: np.uint8(31), 9: np.uint8(30), 10: np.uint8(31), 11: np.uint8(31), 12: np.uint8(31)}


reps = 1
while reps < 100000000:
    calling_function = timeit.timeit(stmt=create_largest_day_dict, number=reps)

    manual_function = timeit.timeit(stmt=manual_dict, number=reps)

    manual_slowness = manual_function / calling_function
    print(f"{manual_slowness=}\t{reps=}")
    reps = reps * 10
