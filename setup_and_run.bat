@echo off
REM Create a virtual environment
echo Creating virtual environment...
py -m venv .venv

REM Activate the virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run the main script
echo Running the project...
python main.py