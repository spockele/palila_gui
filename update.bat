@echo off

set /P choice="Which updates do you want to get? Python only (P), GUI only (G), both (press enter): "

if (%choice%==P) or (not (defined %choice%)) (
REM Script to update all installed python packages and pip
REM  1) Update pip and setuptools
venv\Scripts\python.exe -m pip install --upgrade pip setuptools
REM  2) Gather installed packages
venv\Scripts\python.exe -m pip freeze > update.txt
REM  3) Format the obtained file to force update
venv\Scripts\python.exe -m update_helper
REM  4) Actually update the packages with pip
venv\Scripts\python.exe -m pip install --upgrade -r update.txt
REM  5) Remove the update file
del update.txt
)

if (%choice%==G) or (not (defined %choice%)) ()
REM Also update the repo by pulling the latest
git pull origin main
)

echo.
set /P n="Update succesfull! Press any key to exit. "