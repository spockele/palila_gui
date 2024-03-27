"""
Script to merge all response files in an experiment to one response table file.
Removes the participant ID and shuffles the results. Will not interpret NaN values in the original response files.
Output can be found in the experiment directory, as 'responses_table.csv'.
The table is 1-indexed for all the MATLAB freaks ;)
"""
import pandas as pd
from random import shuffle
import os


# Define the current experiment path and the corresponding responses location.
CURRENT_PATH = os.path.abspath('gui_dev')
RESPONSE_PATH = os.path.join(CURRENT_PATH, 'responses')


if __name__ == '__main__':
    # Create a list to collect the response files
    dfs = list()
    # Collect the response files
    for filepath in os.listdir(RESPONSE_PATH):
        dfs.append(pd.read_csv(os.path.join(RESPONSE_PATH, filepath), index_col=0, header=0, keep_default_na=False))

    # Shuffle the responses
    shuffle(dfs)
    # Concatenate with a loss of index
    out_df = pd.concat(dfs, axis=0, ignore_index=True)
    # Up the index by 1 for the MATLAB people
    out_df.index += 1
    # Write the table to csv file
    out_df.to_csv(os.path.join(CURRENT_PATH, 'responses_table.csv'))
