@echo off
setlocal enabledelayedexpansion

echo Welcome to Kaelys! Run this script to get everything set up.
echo.
echo This script will install the following:
echo - Python 3.13
echo - pip
echo - virtualenv
echo - Git
echo - Dependencies
echo.

:: Ask to install Python
set /p install_python=Do you want to install Python 3.13? (Y/N): 
if /i "!install_python!"=="Y" (
    echo Installing Python 3.13...
    start /wait "" "%USERPROFILE%\Downloads\python-3.13.3-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    echo Waiting for Python to finish installing...

    :checkpython
    where python >nul 2>&1
    if errorlevel 1 (
        timeout /t 5 /nobreak >nul
        goto checkpython
    )

    echo Python install detected!
)

:: Ask to install Git
set /p install_git=Do you want to install Git? (Y/N): 
if /i "!install_git!"=="Y" (
    echo Installing Git...
    winget install --id Git.Git -e --source winget
)

:: Ask to upgrade pip
set /p upgrade_pip=Do you want to upgrade pip? (Y/N): 
if /i "!upgrade_pip!"=="Y" (
    echo Upgrading pip...
    python -m ensurepip
    python -m pip install --upgrade pip
)

:: Ask to create virtual environment
set /p create_venv=Do you want to create a virtual environment? (Y/N): 
if /i "!create_venv!"=="Y" (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Ask to activate virtual environment
set /p activate_venv=Do you want to activate the virtual environment? (Y/N): 
if /i "!activate_venv!"=="Y" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

:: Ask to install dependencies
set /p install_deps=Do you want to install dependencies from requirements.txt? (Y/N): 
if /i "!install_deps!"=="Y" (
    echo Installing requirements...
    pip install -r requirements.txt
)

echo.
echo Setup complete! Bless up.
pause
