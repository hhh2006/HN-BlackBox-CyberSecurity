@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title HN BlackBox // Security Engineering

rem One-time dependency bootstrap. After the first successful setup,
rem normal launches reuse the same local virtual environment.
set "VENV=%LOCALAPPDATA%\HNBlackBox\venv"
set "STAMP=%VENV%\.requirements.sha256"

if not exist "%VENV%\Scripts\python.exe" (
    echo [HN BLACKBOX] First-run setup: creating local Python environment...
    if not exist "%LOCALAPPDATA%\HNBlackBox" mkdir "%LOCALAPPDATA%\HNBlackBox"
    py -3 -m venv "%VENV%" 2>nul
    if errorlevel 1 python -m venv "%VENV%"
    if errorlevel 1 goto :setup_failed
)

for /f "delims=" %%H in ('powershell -NoProfile -Command "(Get-FileHash -Algorithm SHA256 requirements.txt).Hash"') do set "REQHASH=%%H"
set "OLDHASH="
if exist "%STAMP%" set /p OLDHASH=<"%STAMP%"

if /I not "%REQHASH%"=="%OLDHASH%" (
    echo [HN BLACKBOX] Installing/updating dependencies once for this requirements version...
    "%VENV%\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :setup_failed
    >"%STAMP%" echo %REQHASH%
) else (
    echo [HN BLACKBOX] Dependencies already installed. Skipping setup.
)

"%VENV%\Scripts\python.exe" main.py
if errorlevel 1 (
    echo.
    echo [HN BLACKBOX] Application exited with an error.
    pause
)
exit /b %errorlevel%

:setup_failed
echo.
echo [HN BLACKBOX] First-run setup failed.
echo Check that Python 3.11+ is installed and available through 'py' or 'python'.
pause
exit /b 1
