# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[//]: # (## [Unreleased])

[//]: # (### Added)

[//]: # (### Changed)

[//]: # (### Deprecated)

[//]: # (### Removed)

[//]: # (### Fixed)

## [v1.2.1] - tbd

### Added
- The ```demo``` parameter can now be defined as a block to define a custom demonstration screen.
- A first version of the user manual is now included.

### Changed
- The 'Please enter your participant ID' part of the welcome message is now always visible.
- ```text``` is now an optional parameter for the ```Annoyance``` question type.
- An open question (```how_found_other```) is added to the questionnaire for when participants select 'other' in ```how_found```.

### Deprecated
- Experiment configuration information will be removed from the README. This section will not be maintained from v1.2.0.

### Removed
- Removed the ```default_questionnaire.pdf``` document. This information is now included in the manual.


# [v1.2.0] - 28 March 2025

This update contains major back-end changes to the code structure, mainly targeted at duplicate and redundant code. This version also contains some fixes, deprecations and removals in line with planned developements.

### Added
- ```Annoyance``` audio question type, containing the standardised 11-point annoyance question.

### Changed
- Revamp of the progress bar: static regardless of screen, turns green when part is completed, resets when returning to main questionnaire.
- Removed final semicolon \(;\) from the multiple choice, multiple answer question type.
- Removed ```AttributeError``` from ```MultiMulipleChoiceQQuestion```, because it was not relevant.
- Added way to enter multiple ```unlock_condition``` items by using a semicolon.
- Cleanup of the root directory. Moved Python support scripts to their own folder and modified the ```.bat``` scripts.


- FOR DEVELOPERS: this update contains major changes to the Questionnaire and Audio Screen logic, and their underlying management classes. The main changes are the equalisation and merger of both systems. Please refer to the commit history to understand these changes.

### Deprecated
- The Questionnaire ```MultiMultipleChoice``` question type will be removed in future versions. Multiple-choice-multiple-answer questions can be created using the ```MultipleChoice``` type with ```multi = yes```
- Questionnaire question IDs should now be defined in the brackets. They will always be standardised to the ```[part_id]-questionnaire-[question_id]``` format. 

### Removed
- The deprecated keywords ```dependant``` and ```dependant condition``` are now fully removed. They are now defined in the locked question and renamed: ```unlocked by``` and ```unlock condition```.
- ```PointCompassAQuestion``` type has been removed, because it is unnecessarily complex.
- ```filler``` keyword removed from input system, to reflect desired GUI layout behaviour.

### Fixed
- When returning to the main questionnaire from the end screen, the full questionnaire is now accessible.
- Pressing play on an audio now locks the continue button, to avoid the audio playing in the next screen.
- Fixed the ```demo``` screen at the start of the GUI.


## [v1.1.2] - 17 December 2024

### Changed
- Updated Python package dependencies to latest versions.

### Fixed
- Changed configobj version to 5.0.9 in response to fix of [CVE-2023-26112 ReDoS attack vulnerability](https://nvd.nist.gov/vuln/detail/CVE-2023-26112).


## [v1.1.1] - 10 June 2024

### Fixed
Hotfix for a critical navigation issue that makes v1.1.0 unusable.
This issue was related to the incomplete removal of the unused pre-navigation function of the PalilaScreen class


## [v1.1.0] - 3 June 2024 
### !! THIS VERSION DOES NOT WORK !!

### Added
- The number of replays of sound samples is now recorded in the output file:
  - For audio screens with 1 sample: ```<part name>-<audio name>(_<repetition index>)-replays```
  - For audio screens with 2 samples: ```<part name>-<audio name>(_<repetition index>)-replays-left``` and 
```<part name>-<audio name>(_<repetition index>)-replays-right```


- A QuestionManager class to the questionnaire system to get closer to the system of audio questions.
- A ButtonAQuestion superclass for all question types that use buttons to answer (MultipleChoice, IntegerScale, etc.)
- A MultiMultipleChoiceQQuestion class to allow for multiple choice multiple answer questions in Questionnaires.
- Progress bar at the bottom of the screen to show progression through the experiment.
- A script to easily and quickly set up a new experiment.
  

### Changed
- Code restructure to make the audio and questionnaire question systems more uniform. 
  - Answers are now stored directly in a ```QuestionManager.answers```, which is the Layout that holds the Question widgets.
  - Changed the multitude of functions to trigger an answer change to one singular ```change_answer()``` function.
  - The ```change_answer()``` function is now supplemented by a type-specific trigger function per question type.
  - ChoiceButton classes are now functionally the same.
  - questionnaire.py and questionnaire.kv have been split into questionnaire_questions and questionnaire_screen.
  - Logic for splitting the questionnaire over multiple sceens is moved to an external function ```questionnaire_setup()```.


- Change in the logic behind the keywords ```dependant``` and ```dependant condition```:
  - They are now defined in the conditionally unlocked question and renamed: ```unlocked by``` and ```unlock condition```.
  - All question types now allow for conditional locking/unlocking.


- An empty questionnaire block now results in no questionnnaire screen appearing at all.
- Repetition numbering of questions is now 1-indexed instead of 0-indexed.
- Timer now starts when leaving the welcome screen instead of when leaving the startup questionnaire.

### Deprecated
- The keywords ```dependant``` and ```dependant condition``` will be removed in future versions.
  - This version supports the old system where these are defined in the question that conditionally unlocks another.
  - Future versions will only support the new system as described in ```change 2```.

### Removed
- N/A

### Fixed
- Spinner Audio questions did not record their answer to the output file. This is fixed.



## [v1.0.0] - 22 April 2024

First release version of the GUI for the PsychoAcoustic LIstening LAboratory.
