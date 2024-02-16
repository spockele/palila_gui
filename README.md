# Graphical User Interface for PALILA
General GUI for the PALILA listening room

---

## How to run
1. Install Python 3.11 or newer
2. Create a virtual environment (see python docs)
3. Install packages in requirement.txt: ```python -m pip install -r requirements.txt```
4. Run main.py
---

## .palila file structure


```
# ======================================================================================================================

pid = <string>                      # -> Mode to set the Participant ID (auto, input).
welcome = <string> (optional)       # -> Optional welcome message for the first screen.

# ======================================================================================================================

[questionnaire]                     # -> Required section defining the questionnaire at the start of the experiment.
    default = <boolean> (optional)      # -> Switch to set up the questionnaire with default questions.
                                        #    Extra questions can be added to the default list, be aware they require 
                                        #    a manual_screen value.
    manual_split = <boolean> (optional) # -> Switch to set manual splitting of the questions over the screens.
                                        #    In case of manual splitting, each question requires a manual_screen value.
                                        
    [[question <string>]] (optional)    # -> SubSection defining a question in the questionnaire. 
                                        #    <string> defines the name.
        id = <string> (optional)        # -> Optional custom ID for the question in the output file.
                                        #    If not defined, a standardised ID will be assigned
        type = <string>                 # -> Defines the type of question. See below for specifics of each types.
        text = <string>                 # -> Defines the question text.
        manual_screen = <integer>       # -> In case of manual_split = yes, this defines the screen to 
                                        #    put the question. Has no effect if manual_split = no.
        
```

### Some definitions for the above file structure data types:
|----------------|---------------------------------------------------------------|
| ```<string>``` | Any sequence of letters/numbers                               |
| ```<boolean>```| Binary operator (can be: yes, true, on, 1; no, false, off, 0) |
| ```<integer>```| Any number without decimal point                              |
| ```<float>```  | Any number with decimal point                                 |
|----------------|---------------------------------------------------------------|

### The types for questionnaire questions:
QuestionnaireMC: multiple choice questions


Standardised question ID will be structured as follows: ```'{part name}-{audio name}-{question name}'```.\
Or in case of the main questionnaire: ```main-questionnaire-{question name}```.\
All question names will be adjusted to at least 2 characters with ```str().zfill(2)```