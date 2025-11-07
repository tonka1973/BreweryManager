@echo off
REM Brewery Management System - Quick Setup Script for Windows
REM This script automates the installation process

echo ========================================
echo Brewery Management System - Setup
echo ========================================
echo.

REM Check Python installation
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version
echo Python found!
echo.

REM Check Python version
echo [2/4] Verifying Python version (need 3.11+)...
python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Python 3.11 or higher is recommended
    echo Current version may not be compatible
    pause
)
echo.

REM Install dependencies
echo [3/4] Installing dependencies...
echo This may take a few minutes...
echo.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo.
echo Dependencies installed successfully!
echo.

REM Run basic tests
echo [4/4] Running basic tests...
python -c "import tkinter; print('  GUI library (tkinter): OK')"
python -c "import sqlite3; print('  Database (sqlite3): OK')"
python -c "from src.config import constants; print('  Configuration: OK')"
python -c "from src.utilities.auth import AuthManager; print('  Authentication: OK')"
python -c "from src.data_access.sqlite_cache import SQLiteCacheManager; print('  Database manager: OK')"
python -c "from src.gui.main_window import BreweryMainWindow; print('  Main application: OK')"
if errorlevel 1 (
    echo.
    echo WARNING: Some tests failed
    echo The application may not work correctly
    pause
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo The Brewery Management System is ready to use!
echo.
echo To start the application, run:
echo     python main.py
echo.
echo Default login credentials:
echo     Username: admin
echo     Password: admin123
echo.
echo Application data will be stored in:
echo     %USERPROFILE%\.brewerymanager\
echo.
echo For more information, see LOCAL_SETUP_GUIDE.md
echo.
pause
