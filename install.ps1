# ==============================================================================
# install.ps1 - Automated 1-Click Installer for Dynamic Island AI Desktop
# Run via: irm https://raw.githubusercontent.com/ajaybhaaya/dynamic-island-ai/main/install.ps1 | iex
# ==============================================================================

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "         Windows 11 Dynamic Island Desktop AI Companion                " -ForegroundColor White
Write-Host "               Automated 1-Click Setup & Launcher                     " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$repoUrl = "https://github.com/ajaybhaaya/dynamic-island-ai.git"
$targetDir = "$HOME\dynamic-island-ai"

# 1. Target Directory Detection & Download / Clone
if (Test-Path "$PSScriptRoot\main.py") {
    $workDir = $PSScriptRoot
    Set-Location $workDir
} else {
    if (-not (Test-Path $targetDir)) {
        Write-Host "[1/3] Downloading Dynamic Island repository..." -ForegroundColor Yellow
        $hasGit = Get-Command git -ErrorAction SilentlyContinue
        if ($hasGit) {
            git clone $repoUrl $targetDir
        } else {
            Write-Host "      Git not found; downloading archive package from GitHub..." -ForegroundColor Yellow
            $zipPath = "$env:TEMP\dynamic-island-main.zip"
            Invoke-WebRequest -Uri "https://github.com/ajaybhaaya/dynamic-island-ai/archive/refs/heads/main.zip" -OutFile $zipPath
            Expand-Archive -Path $zipPath -DestinationPath "$HOME" -Force
            Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
            if (Test-Path "$HOME\dynamic-island-ai-main") {
                Rename-Item "$HOME\dynamic-island-ai-main" $targetDir -ErrorAction SilentlyContinue
            }
        }
    }
    Set-Location $targetDir
}

Write-Host "[OK] Working Directory: $(Get-Location)" -ForegroundColor Green

# 2. Python Detection
$pyCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pyCmd = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pyCmd = "python"
} else {
    Write-Host "[!] Python was not detected on this system." -ForegroundColor Yellow
    Write-Host "    Installing Python 3.12 automatically via Windows Package Manager..." -ForegroundColor Cyan
    winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $pyCmd = "py"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $pyCmd = "python"
    } else {
        Write-Host "[ERROR] Could not start Python. Please download Python from https://www.python.org/downloads/ and check 'Add python.exe to PATH'." -ForegroundColor Red
        return
    }
}

Write-Host "[2/3] Verifying dependencies using: $pyCmd -m pip..." -ForegroundColor Green
& $pyCmd -m pip install --quiet -r requirements.txt

# 3. Launch Application
Write-Host ""
Write-Host "[3/3] Launching Dynamic Island!" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
& $pyCmd main.py
