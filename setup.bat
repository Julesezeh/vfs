@echo off
REM VFS Booking Bot Setup Script for Windows

echo ================================================================
echo          VFS Appointment Booking Bot - Setup
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Checking Python version...
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Create necessary directories
echo Creating directories...
if not exist logs mkdir logs
if not exist screenshots mkdir screenshots
if not exist config mkdir config
echo Directories created
echo.

REM Copy configuration files
echo Setting up configuration files...

if not exist config\config.yaml (
    if exist config\config.yaml.example (
        copy config\config.yaml.example config\config.yaml
        echo config.yaml created from example
        echo Please edit config\config.yaml with your settings
    ) else (
        echo ERROR: config.yaml.example not found
    )
) else (
    echo config.yaml already exists
)

if not exist config\credentials.yaml (
    if exist config\credentials.yaml.example (
        copy config\credentials.yaml.example config\credentials.yaml
        echo credentials.yaml created from example
        echo Please edit config\credentials.yaml with your details
    ) else (
        echo ERROR: credentials.yaml.example not found
    )
) else (
    echo credentials.yaml already exists
)
echo.

echo ================================================================
echo                    Setup Complete!
echo ================================================================
echo.
echo Next steps:
echo.
echo 1. Edit configuration files:
echo    - config\config.yaml         (Telegram, proxy, settings)
echo    - config\credentials.yaml    (VFS login, applicant info)
echo.
echo 2. Activate virtual environment (if not already activated):
echo    venv\Scripts\activate.bat
echo.
echo 3. Run the bot:
echo    python main.py
echo.
echo For detailed instructions, see:
echo    - QUICKSTART.md (quick setup guide)
echo    - README.md (full documentation)
echo.
echo Good luck!
echo.
pause
