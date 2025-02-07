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

:: Main terminal script to run the GUI


@echo off

.\venv\Scripts\python.exe -c "from GUI import main;main('gui_dev')"

echo.
set /p n="Press enter to exit. "
