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
.\venv\Scripts\python.exe -m pip install -r .\requirements.txt

echo.
set /p n="Setup complete. Press any button to exit setup... "