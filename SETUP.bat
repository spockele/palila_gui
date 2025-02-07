:: Copyright (c) 2025 Josephine Siebert Pockelé
::
:: Licensed under the Apache License, Version 2.0 (the "License");
:: you may not use this file except in compliance with the License.
:: You may obtain a copy of the License at
::
::     http://www.apache.org/licenses/LICENSE-2.0
::
:: Unless required by applicable law or agreed to in writing, software
:: distributed under the License is distributed on an "AS IS" BASIS,
:: WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
:: See the License for the specific language governing permissions and
:: limitations under the License.


@echo off
echo Starting setup for PALILA Graphical User Interface...

if exist .\venv (
	echo Python venv already exists. Continuing...
	) else (
	echo Setting up Python Virtual environment in .\venv
	python -m venv .\venv
	)
echo.
echo Updating virtual environment...
.\venv\Scripts\python.exe -m pip install --upgrade pip setuptools
echo.
echo Installing required Python packages...
.\venv\Scripts\python.exe -m pip install -r .\support_scripts\requirements.txt

echo.
set /p n="Setup complete. Press any button to exit setup... "