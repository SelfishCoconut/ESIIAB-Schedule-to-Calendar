python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Downloading Python installer...
    curl -o python-installer.exe https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe

    echo Installing Python...
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

    echo Cleaning up...
    del python-installer.exe

    echo Python installation completed!
) else (
    echo Python is already installed.

)

REM Create a virtual environment
python -m venv .venv

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Install the requirements
pip install -r requirements.txt

REM Run the main.py script
python main.py

REM Print a message indicating the script has finished running
echo main.py has finished running.