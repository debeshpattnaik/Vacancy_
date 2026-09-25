@echo off
setlocal

echo Starting Legal Vacancy Tracker...

if not exist venv (
    echo Virtual environment not found! Please create it using: python -m venv venv
    exit /b 1
)

call venv\Scripts\activate.bat
python main.py %*

endlocal
