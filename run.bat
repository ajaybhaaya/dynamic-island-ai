@echo off
setlocal enabledelayedexpansion
title Windows 11 Dynamic Island Desktop Companion
cd /d "%~dp0"

echo =======================================================================
echo          Windows 11 Dynamic Island Desktop AI Companion
echo =======================================================================
echo.

:: 1. Detect Python / py launcher
set "PY_CMD="
where py >nul 2>&1
if !ERRORLEVEL! equ 0 (
    set "PY_CMD=py"
) else (
    where python >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set "PY_CMD=python"
    )
)

if not defined PY_CMD (
    echo [!] Python is not detected on this system.
    echo.
    echo Would you like to automatically install Python using Windows Package Manager?
    set /p "AUTO_INSTALL=Install Python now? (Y/N): "
    if /i "!AUTO_INSTALL!"=="Y" (
        echo [*] Installing Python via winget...
        winget install Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
        echo [*] Please close and reopen this terminal after installation completes.
        pause
        exit /b 0
    ) else (
        echo.
        echo Please install Python 3.10+ from https://www.python.org/downloads/
        echo Make sure to check the box: "Add python.exe to PATH" during installation.
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Python detected: !PY_CMD!
!PY_CMD% --version
echo.

:: 2. Check and install dependencies via python -m pip (never fails with 'pip not recognized')
echo [*] Checking required dependencies...
!PY_CMD! -m pip install --quiet -r requirements.txt
if !ERRORLEVEL! neq 0 (
    echo [!] Note: Some packages may need admin rights or took longer. Continuing launch...
)

:: 3. Launch Dynamic Island
echo.
echo [*] Launching Windows 11 Dynamic Island...
!PY_CMD! main.py

if !ERRORLEVEL! neq 0 (
    echo.
    echo [!] Application exited with status code !ERRORLEVEL!.
    pause
)
