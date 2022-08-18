import copy

from text_mining_package import DateFinder

"""
This is the main function for the text mining project.  


"""
if __name__ == "__main__":

    # ~~~~~~~~~~~~~~~~~~~~~~~~
    # read in the source file
    # ~~~~~~~~~~~~~~~~~~~~~~~~
    doc = []
    with open(r'.\dates.txt') as file:
        for line in file:
            doc.append(line)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Run the primary class and create a tuple where the first number is sequential and the 2nd number is text
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pre_sorted_results = []
    for line_counter, line_text in enumerate(doc):
        try:
            pre_sorted_results.append((line_counter, DateFinder(raw_string=line_text).convert_to_python_datetime()))
        except ValueError as uhoh:
            print(f"{uhoh}")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # sort on the date to get the value
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    sorted_results = copy.deepcopy(pre_sorted_results)
    sorted_results.sort(key=lambda x: x[1])
    final_results = [x[0] for x in sorted_results]
