@echo off
REM T-Plexity Streamlit App Startup Script for Windows

echo.
echo Starting T-Plexity Streamlit App...
echo.

REM Check if .env exists
if not exist .env (
    echo Warning: .env file not found. Creating from .env.example...
    if exist .env.example (
        copy .env.example .env
        echo Created .env file
    ) else (
        echo Error: .env.example not found!
        pause
        exit /b 1
    )
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete!
echo Starting Streamlit app...
echo.

REM Start Streamlit
streamlit run app.py

pause

