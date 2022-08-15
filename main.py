import pandas as pd

from text_mining_package import DateFinder

"""
This is the main function for the text mining project.  


"""
if __name__ == "__main__":

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # read in the source file and convert to a series.
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    doc = []
    with open(r'.\dates.txt') as file:
        for line in file:
            doc.append(line)

    medical_dates_df = pd.Series(doc)

    error_counter = 0

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Main Look runs the primary class on each text line, and in case of error, kicks out.
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    for x in range(0, 500):
        text_to_process = doc[x]
        found_date = DateFinder(raw_string=text_to_process)
        try:
            print(f"{x}\t{found_date=}\txxx\t{text_to_process}")
        except ValueError:
            continue

    print(f"{error_counter=}")
    print("fin")
