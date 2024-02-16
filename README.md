# PALILA GUI

Graphical user interface for listening experiments in the 
[<b><u>P</u></b>sycho<b><u>A</u></b>coustic <b><u>LI</u></b>stening <b><u>LA</u></b>boratory (PALILA)](https://iiav.org/content/archives_icsv_last/2023_icsv29/content/papers/papers/full_paper_274_20230331114441190.pdf) 
[[1](#merinomartinez_2023)] at the Delft University of Technology, Faculty of Aerospace Engineering.

### Developed by:
- [ir. Josephine Siebert Pockelé](https://orcid.org/0009-0002-5152-9986)
  - PhD Candidate, [TU Delft Aircraft Noise and Climate Effects Section](https://www.tudelft.nl/lr/organisatie/afdelingen/control-and-operations/aircraft-noise-and-climate-effects-ance).
  - Email: [j.s.pockele@tudelft.nl](mailto:j.s.pockele@tudelft.nl)
  - LinkedIn: [Josephine (Fien) Pockelé](https://www.linkedin.com/in/josephine-pockele)
---
### Requirements
- Windows 10 or 11.
- [Python](https://www.python.org/) version 3.11 or newer.
- A touchscreen device with 16:10 aspect ratio.\
Other ratios may result in visual artefacts.

### Installation
1. Download this software to the desired location, either:
   - through git
   - by downloading the zip file and unpacking it
2. Run ```setup.bat```

Now you can run the GUI with ```PALILA.bat```

---

## Experiment Configuration
The experiment configuration consists of two items:
- An experiment config file (```<experiment_name>.palila```)
  - Defines the experiment (audios, questions, etc.).
- An experiment file directory (```.\<experiment_name>```)
  - Contains the audio samples and the responses of the experiment.

### Config file structure (```.palila```)
```
# ======================================================================================================================

pid = <string>                      # -> Mode to set the Participant ID (auto, input).
welcome = <string> (optional)       # -> Optional welcome message for the first screen.
randomise = <boolean> (optional)    # -> Switch to randomise the order of the experiment parts.

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

# ======================================================================================================================
        
[part <string>]                     # -> Required section defining a part of the experiment (grouping of audios).
                                    #   Multiple parts per experiment are allowed.
    randomise = <boolean> (optional)    # -> Switch to randomise the order of the audios within the part.
    intro = <string> (optional)         # -> Optional introduction message to the experiment part.
    
    [[audio <string>]]                  # -> SubSection defining the screen for one audio sample.
                                        #   Multiple audios per part are allowed
        filename = <string>                 # -> Name of the audio file inside the experiment directory.
        max replays = <integer> (optional)  # -> Defines the maximum number of times a sample can be replayed.
                                            #   Defaults to 1.
                                            
        [[[question <string>]]]             # -> SubSubSection defining a single question for the audio sample.
            type = <string>                     # -> Defines the type of question. 
                                                #   See below for specifics of each types.
            text = <string>                     # -> Defines the question text.

# ======================================================================================================================
```


### Some definitions of the data types:
|   Value type    |                      Explanation                      |
|:---------------:|:-----------------------------------------------------:|
| ```<string>```  |           Any sequence of letters / numbers           |
| ```<boolean>``` | Binary operator (yes, true, on, 1; no, false, off, 0) |
| ```<integer>``` |           Any number without decimal point            |
|  ```<float>```  |             Any number with decimal point             |


### The questionnaire question types:
- ```FreeNum```: Question asking for a freely entered numerical value.
    - Requires no additional input.
- ```QuestionnaireMC```: Multiple choice question with buttons.
    - Requires: ```choices = <string>, <string>, ...``` -> Defines the choice buttons.
    - Recommended limit of 4-5 choices.
- ```Spinner```: Multiple choice question with a dropdown menu.
    - Requires: ```choices = <string>, <string>, ...``` -> Defines the dropdown items.

### The audio question types:
- ```Text```: Just text, no question.
    - Requires no additional input.
- ```AudioMC```: Multiple choice question with buttons.
    - Requires: ```choices = <string>, <string>, ...``` -> Defines the choice buttons.
    - Recommended limit of 4-5 choices.
- ```NumScale```: Rating question with an integer numerical scale.
    - Requires:\
```min = <integer>``` -> Defines the minimum value of the scale\
```max = <integer>``` -> Defines the minimum value of the scale
    - Recommended range: ```4 <= (max - min) <= 10```
    - Optional:\
```left note = <string>``` -> Defines the text on the left side of the scale\
```right note = <string>``` -> Defines the text on the right side of the scale

### Standardised question IDs
- In the main questionnaire: ```main-questionnaire-{question name}```.
- In ```[audio]``` sections: ```{part name}-{audio name}-{question name}```.
- In part questionnaires: ```{part name}-questionnaire-{question name}```.
- All question, audio and part names will be adjusted to at least 2 characters with ```str().zfill(2)```.

---
## Output file format
Results from an experiment will be output as individual ```.csv``` files in the directory ```.\<experiment name>\responses\```.\
The ```.csv``` files contain a table which is formated as follows:

| ```<experiment_name>``` | ```<question ID>``` | ```<question ID>``` | ... |
|------------------------:|:-------------------:|:-------------------:|-----|
|  ```<Participant ID>``` |   ```<answer>```    |  ``` <answer> ```   | ... |

A script will be included to merge these individual tables into one ```.csv``` file, with a row per participant ID:

| ```<experiment_name>``` | ```<question ID>``` | ```<question ID>``` | ... |
|:-----------------------:|:-------------------:|:-------------------:|-----|
| ```<Participant ID>```  |   ```<answer>```    |  ``` <answer> ```   | ... |
| ```<Participant ID>```  |   ```<answer>```    |  ``` <answer> ```   | ... |
|           ...           |         ...         |         ...         | ... |

[//]: # (---)

[//]: # (## Publications using this code)

---
## References
<a id="merinomartinez_2023"> [1] R. Merino-Martínez, B. von den Hoff, and D. G. Simons, ‘Design and Acoustic Characterization of a Psycho-acoustic listening facility’, in Proceedings of the 29th international congress on sound and vibration, E. Carletti, Ed., Prague, Czech Republic: IIAV CZECH s.r.o., Jul. 2023, pp. 274–281.</a>
