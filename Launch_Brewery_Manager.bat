@echo off
REM Brewery Manager Launcher
REM Double-click this file to start the application

cd /d "%~dp0"
echo ========================================
echo   BREWERY MANAGER
echo ========================================
echo.
echo Starting application...
echo.

python main.py

REM If Python fails, try python3
if errorlevel 1 (
    echo.
    echo Python command failed, trying python3...
    python3 main.py
)

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Failed to launch application
    echo ========================================
    echo.
    echo Possible causes:
    echo  - Python not installed
    echo  - Dependencies not installed
    echo.
    echo Press any key to close...
    pause >nul
)
