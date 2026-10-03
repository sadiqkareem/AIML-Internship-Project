@echo off
setlocal
echo ========================================================
echo         Starting AI Writer Web Application
echo ========================================================

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    python -m venv .venv
    echo Installing dependencies...
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting server on http://localhost:5000 ...
python app.py
pause
