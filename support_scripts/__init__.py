"""
Scripts to support the GUI.
"""

# Copyright (c) 2024 Josephine Siebert Pockelé
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from random import shuffle
import pandas as pd
import os


def merge_responses():
    """
    Merge experiment response files into one csv table.
    """
    experiment = input('Enter the name of the experiment: ')
    # Define the current experiment path and the corresponding responses location.
    current_path = os.path.abspath(experiment)
    response_path = os.path.join(current_path, 'responses')

    # Create a list to collect the response files
    dfs = list()

    # Collect the response files
    for filepath in os.listdir(response_path):
        dfs.append(pd.read_csv(os.path.join(response_path, filepath), index_col=0, header=0, keep_default_na=False))

    # Shuffle the responses
    shuffle(dfs)
    # Concatenate with a loss of index
    out_df = pd.concat(dfs, axis=0, ignore_index=True)
    # Up the index by 1 for the MATLAB people
    out_df.index += 1
    # Write the table to csv file
    out_df.to_csv(os.path.join(current_path, 'responses_table.csv'))
