@echo off
title Create Dynamic Island Shortcuts
cd /d "%~dp0"

echo [*] Creating Desktop and Start Menu shortcuts for Dynamic Island...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $d = $ws.CreateShortcut([IO.Path]::Combine($env:USERPROFILE, 'Desktop', 'Dynamic Island.lnk')); $d.TargetPath = [IO.Path]::Combine((Get-Location).Path, 'run.bat'); $d.WorkingDirectory = (Get-Location).Path; $d.Description = 'Windows 11 Dynamic Island Desktop AI Companion'; $d.Save(); $sm = [Environment]::GetFolderPath('StartMenu'); $p = Join-Path $sm 'Programs'; $s = $ws.CreateShortcut((Join-Path $p 'Dynamic Island.lnk')); $s.TargetPath = [IO.Path]::Combine((Get-Location).Path, 'run.bat'); $s.WorkingDirectory = (Get-Location).Path; $s.Description = 'Windows 11 Dynamic Island'; $s.Save(); Write-Host '[SUCCESS] Shortcuts created on Desktop and Start Menu!' -ForegroundColor Green"

echo.
pause
