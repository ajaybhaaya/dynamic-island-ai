@echo off
title Windows 11 Dynamic Island Desktop Companion
cd /d "%~dp0"

echo =======================================================================
echo          Windows 11 Dynamic Island Desktop AI Companion
echo =======================================================================
echo.

:: 1. Search for Python
set "PYTHON_EXE="

:: Try 'py -3' or 'py'
py -3 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=py -3"
    goto :FOUND_PYTHON
)

py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=py"
    goto :FOUND_PYTHON
)

:: Try 'python'
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=python"
    goto :FOUND_PYTHON
)

:: Try 'python3'
python3 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=python3"
    goto :FOUND_PYTHON
)

:: Check Local AppData default installation paths
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_EXE=%%D\python.exe"
        goto :FOUND_PYTHON
    )
)

for /d %%D in ("%ProgramFiles%\Python*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_EXE=%%D\python.exe"
        goto :FOUND_PYTHON
    )
)

:NOT_FOUND
echo [!] Python is not detected on your system.
echo [*] Attempting to install Python 3.12 automatically via Windows Package Manager...
echo.
winget install Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
if %ERRORLEVEL% equ 0 (
    echo.
    echo [*] Python installed successfully! Please restart this script.
    pause
    exit /b 0
)

echo.
echo [ERROR] Could not install Python automatically.
echo Please download Python 3.10+ from: https://www.python.org/downloads/
echo IMPORTANT: During setup, make sure to check: "Add python.exe to PATH"
echo.
pause
exit /b 1

:FOUND_PYTHON
echo [OK] Using Python: %PYTHON_EXE%
%PYTHON_EXE% --version
echo.

:: 2. Ensure pip is installed
%PYTHON_EXE% -m pip --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [*] Setting up pip module...
    %PYTHON_EXE% -m ensurepip --default-pip >nul 2>&1
)

:: 3. Install/verify requirements
echo [*] Verifying dependencies (PySide6, psutil, mss, Pillow, requests)...
%PYTHON_EXE% -m pip install --quiet -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [!] Standard install had warnings; attempting user install...
    %PYTHON_EXE% -m pip install --user --quiet -r requirements.txt
)

:: 4. Optional: Create desktop and start menu shortcuts if missing
if not exist "%USERPROFILE%\Desktop\Dynamic Island.lnk" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([IO.Path]::Combine($env:USERPROFILE, 'Desktop', 'Dynamic Island.lnk')); $s.TargetPath = [IO.Path]::Combine((Get-Location).Path, 'run.bat'); $s.WorkingDirectory = (Get-Location).Path; $s.Description = 'Windows 11 Dynamic Island'; $s.Save()" >nul 2>&1
)

:: 5. Launch Application
echo.
echo =======================================================================
echo [*] Starting Dynamic Island...
echo =======================================================================
%PYTHON_EXE% main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Dynamic Island exited with code %ERRORLEVEL%.
    pause
)
