# PALILA GUI

Graphical user interface for listening experiments in the
[<b><u>P</u></b>sycho<b><u>A</u></b>coustic <b><u>LI</u></b>stening <b><u>LA</u></b>boratory (PALILA)](https://iiav.org/content/archives_icsv_last/2023_icsv29/content/papers/papers/full_paper_274_20230331114441190.pdf)
[[1](#merinomartinez_2023)] at the [Delft University of Technology, Faculty of Aerospace Engineering](https://www.tudelft.nl/lr).

![GitHub Release](https://img.shields.io/github/v/release/spockele/palila_gui?logo=github) [![DOI](https://zenodo.org/badge/789127892.svg)](https://zenodo.org/doi/10.5281/zenodo.11028965) ![GitHub License](https://img.shields.io/github/license/spockele/palila_gui) ![GitHub language count](https://img.shields.io/github/languages/top/spockele/palila_gui)

### Developed by:
- [ir. Josephine Siebert Pockelé](https://orcid.org/0009-0002-5152-9986)
  - PhD Candidate, [TU Delft Aircraft Noise and Climate Effects Section](https://www.tudelft.nl/lr/organisatie/afdelingen/control-and-operations/aircraft-noise-and-climate-effects-ance).
  - Email: [j.s.pockele@tudelft.nl](mailto:j.s.pockele@tudelft.nl)
  - LinkedIn: [Josephine (Fien) Pockelé](https://www.linkedin.com/in/josephine-pockele)
---
### Requirements
- Windows 10 or 11.
- [Python](https://www.python.org/) version 3.11 or newer. 
  - Enable <b><u>'Add Python to PATH'</u></b> while installing.
- A touchscreen device with a resolution of 1920 x 1200 at 100% screen scaling.
  - Other resolutions will result in visual defects.

### Installation
1. Download this software to the desired location, either:
   - through git
   - by downloading the zip file and unpacking it
2. Run ```setup.bat```

Now you can run the GUI with ```PALILA.bat```

---

### Copyright notice

Technische Universiteit Delft hereby disclaims all copyright interest in the program “PALILA GUI”, a graphical user interface software for psychoacoustic listening epxeriments, written by the Author(s). 
Henri Werij, Faculty of Aerospace Engineering, Technische Universiteit Delft. 

Copyright (c) 2024, Josephine Siebert Pockelé

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

### Citation
If you use this code for published research, please cite it as below:
```
Pockelé, J.S. (2024). Graphical User Interface for the Psychoacoustic Listening Laboratory (PALILA GUI) (version v1.1.0). Zenodo. DOI: 10.5281/zenodo.11028965.
```

---
## Experiment Configuration
The experiment configuration consists of the following files in this directory, where ```<experiment name>``` represents the name you use for your experiment:
- An experiment configuration file (```<experiment name>.palila```)
  - Defines the experiment (audios, questions, etc.).
  - An example can be found in ```gui_dev.palila```.
  - The structure of this file is described in the [following section](#configfile_structure).
- An experiment file directory (```.\<experiment name>```)
  - Contains the audio samples and the responses of the experiment.
  - See for example the ```.\gui_dev``` directory.

The script ```setup_new.bat``` will create the configuration file and experiment file directory for you, and do the necessary modification in the code for it to run.


### Config file structure (```.palila```)
<a id="configfile_structure"></a>
```
# ======================================================================================================================

pid mode = <string>                 # -> Mode to set the Participant ID (auto, input).
welcome = <string> (optional)       # -> Optional welcome message for the first screen.
goodbye = <string> (optional)       # -> Optional goodbye message for the final screen.
randomise = <boolean> (optional)    # -> Switch to randomise the order of the experiment parts.
demo = <boolean> (optional)         # -> Show a demonstration for participants before the welcome screen.

# ======================================================================================================================

[questionnaire]                     # -> Required section defining the questionnaire at the start of the experiment.
                                    #   Will always show up, but if empty: there will only be a default message.
    default = <boolean> (optional)      # -> Switch to set up the questionnaire with default questions.
                                        #   Extra questions can be added to the default list, be aware they require 
                                        #   a manual screen value.
    manual split = <boolean> (optional) # -> Switch to set manual splitting of the questions over the screens.
                                        #   In case of manual splitting, each question requires a manual screen value.
                                        
    [[question <string>]] (optional)    # -> SubSection defining a question in the questionnaire. 
                                        #   <string> defines the name.
        id = <string> (optional)            # -> Optional custom ID for the question in the output file.
                                            #   If not defined, a standardised ID will be assigned
        type = <string>                     # -> Defines the type of question. See below for specifics of each types.
        text = <string>                     # -> Defines the question text.
        manual screen = <integer>           # -> In case of manual split = yes, this defines the screen to 
                                            #   put the question. Has no effect if manual split = no.
                                            
        unlocked by = <string>  (optional)            # -> Question ID of another questionnaire question, which locks 
                                                      #   this question until the answer in the other question equals 
                                                      #   the value in 'unlock condition'.
        unlock condition = <string>  (optional)       # -> The value the answer of the unlocking question has to take 
                                                      #   to unlock this question.

# ======================================================================================================================
        
[part <string>]                     # -> Required section defining a part of the experiment (grouping of audios).
                                    #   Multiple parts per experiment are allowed.
    randomise = <boolean> (optional)    # -> Switch to randomise the order of the audios within the part.
    
    [[breaks]] (optional)               # -> Optional breaks to allow for resting in the experiment part.
        text = <string> (optional)          # -> Optional custom message for during the breaks.
        interval = <integer>                # -> Number of audios between breaks.
                                            #   [0]: Adds a break only at the end of the part.
                                            #   [1, ...]: Adds a break every n audios and at the end of the part.
                                            #   [-1, ...]: Same, but a break at the end of the part is omitted.
        time = <integer>                    # -> Duration of the breaks in seconds.
    
    [[intro]] (optional)                # -> Optional introduction message to the experiment part.
        text = <string>                     # -> Introduction message text.
        time = <integer>                    # -> Duration of the intro timer in seconds.
        
    [[questions]] (optional)            # -> Optional SubSection to define the questions for all audios in this part.
                                        #   See below how to define questions. Questions in [Audio <string>] will be 
                                        #   ignored if this SubSection is defined.
    
    [[audio <string>]]                  # -> SubSection defining the screen for one audio sample.
                                        #   Multiple audios per part are allowed
        filename = <string>                 # -> Name of the audio file inside the experiment directory.
        filename_2 = <string> (optional)    # -> Optional second audio file for comparisons. Will add an extra play 
                                            #   button to the AudioQuestionScreen.
        max replays = <integer> (optional)  # -> Defines the maximum number of times a sample can be replayed.
                                            #   Defaults to 1.
        repeat = <integer> (optional)       # -> Defines the number of times this audio is repeated in the part.
                                            #   Defaults to 1.
                                            
        unlocked by = <string>  (optional)            # -> Question ID of another audio question, which locks 
                                                      #   this question until the answer in the other question 
                                                      #   equals the value in 'unlock condition'.
        unlock condition = <string>  (optional)       # -> The value the answer of the unlocking question has to take 
                                                      #   to unlock this question.
                                            
        [[[question <string>]]]             # -> SubSubSection defining a single question for the audio sample.
            type = <string>                     # -> Defines the type of question. 
                                                #   See below for specifics of each types.
            text = <string>                     # -> Defines the question text.
            
    [[questionnaire]] (optional)        # -> SubSection defining the optional questionnaire of this experiment part.
                                        #   See the main questionnaire for syntax. Keyword 'default' is disabled.

# ======================================================================================================================
```


### Some definitions of the data types:
|   Value type    |                      Explanation                      |
|:---------------:|:-----------------------------------------------------:|
| ```<string>```  |              Any sequence of characters               |
| ```<boolean>``` | Binary operator (yes, true, on, 1; no, false, off, 0) |
| ```<integer>``` |           Any number without decimal point            |
|  ```<float>```  |             Any number with decimal point             |


### The questionnaire question types:
- ```FreeNumber```: Question asking for a freely entered numerical value.
  - Requires no additional input.


- ```FreeText```: Question asking for a freely entered answer (can be anything, maximum 2 lines).
  - Requires no additional input.


- ```MultipleChoice```: Multiple choice question with buttons.
  - Requires: ```choices = <string>, <string>, ...``` -> Defines the choice buttons.
  - Recommended limit of 4-5 choices.


- ```MultiMultipleChoice```: Multiple choice, multiple answer question with buttons.
  - Requires: ```choices = <string>, <string>, ...``` -> Defines the choice buttons.
  - Recommended limit of 4-5 choices.
  - Records all selected answers separated by a semicolon (```;```)


- ```Spinner```: Multiple choice question with a dropdown menu.
  - Requires: ```choices = <string>, <string>, ...``` -> Defines the dropdown items.

### The audio question types:
- ```Text```: Just text, no question.
  - Requires no additional inputs.


- ```MultipleChoice```: Multiple choice question with buttons.
  - Requires: ```choices = <string>, <string>, ...``` -> Defines the choice buttons.
  - Recommended limit of 4-5 choices.


- ```Spinner```: Multiple choice question with a dropdown menu.
  - Requires: ```choices = <string>, <string>, ...``` -> Defines the dropdown items.


- ```IntegerScale```: Rating question with an integer numerical scale.
  - Requires the following arguments:\
    ```min = <integer>``` -> Defines the minimum value of the scale.\
    ```max = <integer>``` -> Defines the minimum value of the scale.
  - Recommended range: ```4 <= (max - min) <= 8 with left and right note, else 6 <= (max - min) <= 10```
  - Optional:\
    ```left note = <string>``` -> Defines the text on the left side of the scale.\
    ```right note = <string>``` -> Defines the text on the right side of the scale.


- ```Slider```: Rating question with a slider input.
  - Requires the following arguments:\
    ```min = <float>``` -> Defines the minimum value of the scale.\
    ```max = <float>``` -> Defines the minimum value of the scale.\
    ```step = <float>``` -> Defines the steps of the slider scale.
  - Recommended to use only after NumScale does not suffice in resolution.
  - Optional:\
    ```left note = <string>``` -> Defines the text on the left side of the scale.\
    ```right note = <string>``` -> Defines the text on the right side of the scale.


- ```PointCompass```: A question with an 8-point direction compass to test directionality.
  - Requires no additional input arguments.
---
## Output file format
Results from an experiment will be output as individual ```.csv``` files in the directory 
```.\<experiment name>\responses\```.\
The ```.csv``` files contain a table which is structured as follows:

|          | ```<question ID>``` | ```<question ID>``` | ... |            Timer            |
|:--------:|:-------------------:|:-------------------:|-----|:---------------------------:|
| response |   ```<answer>```    |  ``` <answer> ```   | ... | ```<Completion Time> [s]``` |

The individual response files can be merged into a single ```.csv``` file using the ```.\merge_responses.bat``` script. This script requires modifying Line 27 in ```.\merge_responses.py``` to:
```
CURRENT_PATH = os.path.abspath('<experiment_name>')
```
The resulting ```.\<experiment_name>\responses_table.csv``` file will contain a table structured as follows:

|     | ```<question ID>``` | ```<question ID>``` | ... |            Timer            |
|:---:|:-------------------:|:-------------------:|-----|:---------------------------:|
|  0  |   ```<answer>```    |  ``` <answer> ```   | ... | ```<Completion Time> [s]``` |
|  1  |   ```<answer>```    |  ``` <answer> ```   | ... | ```<Completion Time> [s]``` |
| ... |         ...         |         ...         | ... |             ...             |

### Standardised question IDs
For all audio questions, and for questionnaire questions with no custom ID, a standardised ```<question ID>``` will 
be generated. The format is defined:
- In the main questionnaire: ```main-questionnaire-<question name>```.
- In part questionnaires: ```<part name>-questionnaire-<question name>```.
- For audio questions: ```<part name>-<audio name>-<question name>```.
- All question, audio and part names will be adjusted to at least 2 characters with ```str().zfill(2)```.

The names (part, audio and question) are the ```<string>``` values defined in the brackets of the input file.\
<b>NOTE</b>: When ```repeat``` is set in an ```[audio]``` section, a two digit (01, 02, ...) ```<repetition index>``` is
added between the audio and question name as follows:```<part name>-<audio name>_<repetition index>-<question name>```.

### Storing of audio replays
In case an audio sample can be replayed, the number of replays is stored under the following ```<question ID>``` format:
- For audio screens with 1 sample: ```<part name>-<audio name>(_<repetition index>)-replays```
- For audio screens with 2 samples: ```<part name>-<audio name>(_<repetition index>)-replays-left``` and 
```<part name>-<audio name>(_<repetition index>)-replays-right```, where 'left' and 'right' correspond to ```filename``` and ```filename_2```, respectively.

[//]: # (---)

[//]: # (## Publications using this code)

---
## References
<a id="merinomartinez_2023"> [1] R. Merino-Martínez, B. von den Hoff, and D. G. Simons, ‘Design and Acoustic Characterization of a Psycho-acoustic listening facility’, in Proceedings of the 29th international congress on sound and vibration, E. Carletti, Ed., Prague, Czech Republic: IIAV CZECH s.r.o., Jul. 2023, pp. 274–281.</a>
