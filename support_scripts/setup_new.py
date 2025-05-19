"""
Script to quickly set up a new experiment in the GUI.
"""

# Copyright (c) 2025 Josephine Siebert Pockelé
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

import shutil
import os


# String for a basic new .palila file that works
NEW_STRING = """## This is your experiment input file.
## It is set up with a basic structure for a PALILA GUI experiment.

pid mode = auto
randomise = no
demo = no

[questionnaire]
\tdefault = yes

[part 0]
\trandomise = yes
    
\t[[questions]]
\t\t[[[question annoyance]]]
\t\t\ttype = Annoyance

\t[[audio 0]]
\t\tfilename = 'tone500Hz.wav'

"""


def main():
    """
    Run function of this script.
    """
    # Ask user for the experiment name.
    experiment_name = input('Enter a name for your experiment: ')

    # Don't do any of these actions in case of gui_dev
    if not experiment_name == 'gui_dev':
        # Check if an experiment directory with this name already exists.
        if os.path.isdir(experiment_name):
            # Ask for permission to remove the directory.
            rm_dir = input('An experiment directory with this name already exists. '
                           'Do you want to overwrite it? (yes/no): ')
            if rm_dir.lower() in ('yes', 'y'):
                # Remove and recreate if permission is given.
                shutil.rmtree(experiment_name)
                os.mkdir(experiment_name)
            else:
                # Otherwise, do nothing.
                print(f'Not overwriting the experiment directory {experiment_name}.')
        else:
            # Create a new directory if it doesn't exist yet.
            os.mkdir(experiment_name)

        # Check if an input file already exists for this experiment name.
        if os.path.isfile(f'{experiment_name}.palila'):
            # Ask for permission to remove the input file.
            rm_file = input('An experiment input file with this name already exists. '
                            'Do you want to overwrite it? (yes/no): ')
            if rm_file.lower() in ('yes', 'y'):
                # Remove and recreate if permission is given.
                os.remove(f'{experiment_name}.palila')
                with open(f'{experiment_name}.palila', 'w') as palila_file:
                    palila_file.writelines(NEW_STRING)
            else:
                # Otherwise, do nothing.
                print(f'Not overwriting the experiment input file {experiment_name}.palila.')
        else:
            # Create a new input file if it doesn't exist yet.
            with open(f'{experiment_name}.palila', 'w') as palila_file:
                palila_file.writelines(NEW_STRING)

        # Copy the tone file to the experiment directory
        shutil.copyfile('gui_dev/tone500Hz.wav', f'{experiment_name}/tone500Hz.wav')

    # Read the current main python file of the GUI
    with open('PALILA.bat', 'r') as bat_file:
        lines = bat_file.readlines()
    # Overwrite the run line in the main python file
    for li, line in enumerate(lines):
        if "from GUI import main" in line:
            current_name = line.split("\'")[1]
            lines[li] = line.replace(current_name, experiment_name)

    # Rewrite the main python file
    with open('PALILA.bat', 'w') as bat_file:
        bat_file.writelines(lines)
