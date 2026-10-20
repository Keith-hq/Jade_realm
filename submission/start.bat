@echo off
chcp 65001 >nul
title Jade Culture Hub

echo ==========================================
echo   文化基因库与时空地图 - Jade Culture Hub
echo ==========================================
echo.

:: Find Python
set PYTHON=
set PIP=

:: Try python3 first (common on newer installs)
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=python3
    set PIP=pip3
    goto :found
)

:: Try python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=python
    set PIP=pip
    goto :found
)

:: Try py launcher (Windows standard)
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=py
    set PIP=py -m pip
    goto :found
)

:: Try common paths
if exist "C:\Python312\python.exe" (
    set PYTHON=C:\Python312\python.exe
    set PIP=C:\Python312\python.exe -m pip
    goto :found
)
if exist "C:\Python311\python.exe" (
    set PYTHON=C:\Python311\python.exe
    set PIP=C:\Python311\python.exe -m pip
    goto :found
)
if exist "C:\Python310\python.exe" (
    set PYTHON=C:\Python310\python.exe
    set PIP=C:\Python310\python.exe -m pip
    goto :found
)

:: Try Microsoft Store path
for /d %%i in ("%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.*") do (
    if exist "%%i\python.exe" (
        set PYTHON=%%i\python.exe
        set PIP=%%i\python.exe -m pip
        goto :found
    )
)

echo [ERROR] Python not found.
echo.
echo Please install Python from https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:found
echo Python found: %PYTHON%
echo.

echo [1/2] Installing dependencies...
cd /d "%~dp0backend"
%PIP% install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [WARNING] pip install failed, trying with --user flag...
    %PIP% install -r requirements.txt --user -q
)

echo [2/2] Starting server...
echo Browser will open automatically once ready.
echo.
%PYTHON% main.py

pause
