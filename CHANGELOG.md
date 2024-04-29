# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added
- Added a QuestionManager class to the questionnaire system to get closer to the system of audio questions.
- Created a ButtonAQuestion superclass for all question types that use buttons to answer (MultipleChoice, IntegerScale, etc.)

### Changed
- Code restructure to make the audio and questionnaire question systems more uniform. 
  - Answers are now stored directly in a ```QuestionManager.answers```, which is the Layout that holds the Question widgets.
  - Changed the multitude of functions to trigger an answer change to one singular ```change_answer()``` function.
  - The ```change_answer()``` function is now supplemented by a type-specific trigger function per question type.
  - ChoiceButton classes are now functionally the same.
  - questionnaire.py and questionnaire.kv have been split into questionnaire_questions and questionnaire_screen.
  - Logic for splitting the questionnaire over multiple sceens is moved to an external function ```questionnaire_setup()```.

- Repetition numbering of questions is now 1-indexed instead of 0-indexed.

### Deprecated


### Removed
- AnswerHolder removed from audio_questions.py.


### Fixed


### Security



## [v1.0.0] - 22 April 2024

First release version of the GUI for the PsychoAcoustic LIstening LAboratory.
