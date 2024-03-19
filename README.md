# PALILA GUI

Graphical user interface for listening experiments in the
[<b><u>P</u></b>sycho<b><u>A</u></b>coustic <b><u>LI</u></b>stening <b><u>LA</u></b>boratory (PALILA)](https://iiav.org/content/archives_icsv_last/2023_icsv29/content/papers/papers/full_paper_274_20230331114441190.pdf)
[[1](#merinomartinez_2023)] at the [Delft University of Technology, Faculty of Aerospace Engineering](https://www.tudelft.nl/lr).

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
- A touchscreen device with a resolution of 1920 x 1200.
  - Other resolutions will result in visual defects.

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

pid mode = <string>                 # -> Mode to set the Participant ID (auto, input).
welcome = <string> (optional)       # -> Optional welcome message for the first screen.
goodbye = <string> (optional)       # -> Optional goodbye message for the final screen.
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
                                            #
        dependant = <string>  (optional)              # -> Question ID of another questionnaire question, which is 
                                                      #   locked until the condition in this question is met.
        dependant condition = <string>  (optional)    # -> The value the answer of this question has to take to unlock 
                                                      #   the dependant question.

# ======================================================================================================================
        
[part <string>]                     # -> Required section defining a part of the experiment (grouping of audios).
                                    #   Multiple parts per experiment are allowed.
    randomise = <boolean> (optional)    # -> Switch to randomise the order of the audios within the part.
    
    [[breaks]] (optional)               # -> Optional breaks to allow for resting in the experiment part.
        text = <string> (optional)          # -> Optional custom message for during the breaks.
        interval = <integer>                # -> Number of audios between breaks.
        time = <integer>                    # -> Duration of the breaks in seconds.
    
    [[intro]] (optional)                # -> Optional introduction message to the experiment part.
        text = <string>                     # -> Introduction message text.
        time = <integer>                      # -> Duration of the intro timer in seconds.
        
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
The ```.csv``` files contain a table which is formated as follows:

|          | ```<question ID>``` | ```<question ID>``` | ... |            Timer            |
|:--------:|:-------------------:|:-------------------:|-----|:---------------------------:|
| response |   ```<answer>```    |  ``` <answer> ```   | ... | ```<Completion Time> [s]``` |

A script will be included to merge these individual tables into one ```.csv``` file, with a row per participant ID:

|                        | ```<question ID>``` | ```<question ID>``` | ... |            Timer            |
|:----------------------:|:-------------------:|:-------------------:|-----|:---------------------------:|
| ```<Participant ID>``` |   ```<answer>```    |  ``` <answer> ```   | ... | ```<Completion Time> [s]``` |
| ```<Participant ID>``` |   ```<answer>```    |  ``` <answer> ```   | ... | ```<Completion Time> [s]``` |
|          ...           |         ...         |         ...         | ... |             ...             |

### Standardised question IDs
For all audio questions, and the questionnaire questions where no ID is defined, a standardised format ID will 
be generated. The format is defined:
- In the main questionnaire: ```main-questionnaire-{question name}```.
- In ```[audio]``` sections: ```{part name}-{audio name}-{question name}```.
- In part questionnaires: ```{part name}-questionnaire-{question name}```.
- All question, audio and part names will be adjusted to at least 2 characters with ```str().zfill(2)```.

The names (part, audio and question) are the ```<string>``` values defined in the brackets of the input file.\
<b>NOTE</b>: When ```repeat``` is set in an ```[audio]``` section, a two digit (01, 02, ...) repetition index is added 
as follows: ```{part name}-{audio name}_{repetition index}-{question name}``` to all repetitions of the same question.

[//]: # (---)

[//]: # (## Publications using this code)

---
## References
<a id="merinomartinez_2023"> [1] R. Merino-Martínez, B. von den Hoff, and D. G. Simons, ‘Design and Acoustic Characterization of a Psycho-acoustic listening facility’, in Proceedings of the 29th international congress on sound and vibration, E. Carletti, Ed., Prague, Czech Republic: IIAV CZECH s.r.o., Jul. 2023, pp. 274–281.</a>
