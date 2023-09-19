@echo off

python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! First install python and then try again later.
    pause
    exit
)

python -c "import selenium" >nul 2>&1
if errorlevel 1 (
    echo Installing selenium package...
    pip install selenium
)

python -u aims.py