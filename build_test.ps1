# Local Build Test Script for Simple Audio Player
# Replicates the GitHub Actions release.yml workflow steps on Windows

$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Starting Local Build Workflow Test..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Resolve Python version (prefers 3.11 if available)
Write-Host "[1/7] Detecting Python environment..." -ForegroundColor Yellow
$PYTHON_EXE = "python"

try {
    $testOutput = & py -3.11 -V 2>$null
    if ($testOutput -like "*3.11*") {
        $PYTHON_EXE = "py -3.11"
        Write-Host "Detected Python 3.11 via launcher (py -3.11)" -ForegroundColor Green
    } else {
        $pythonVer = & python -V 2>$null
        Write-Host "Using default python command (Found: $pythonVer)" -ForegroundColor Green
    }
} catch {
    $pythonVer = & python -V 2>$null
    Write-Host "Using default python command (Found: $pythonVer)" -ForegroundColor Green
}

# Define command wrapper to execute Python commands correctly
function Invoke-PythonCommand {
    param([string]$Arguments)
    if ($PYTHON_EXE -eq "py -3.11") {
        & py -3.11 ( -split $Arguments )
    } else {
        & python ( -split $Arguments )
    }
}

# 2. Extract Version from info.json
Write-Host "[2/7] Extracting version from info.json..." -ForegroundColor Yellow
if (-not (Test-Path "info.json")) {
    Write-Error "info.json not found in the root directory."
}
$info = Get-Content -Raw -Path "info.json" | ConvertFrom-Json
$VERSION = $info.version
Write-Host "Target Version: $VERSION" -ForegroundColor Green

# 3. Install/Update dependencies
Write-Host "[3/7] Upgrading pip and installing requirements..." -ForegroundColor Yellow
Invoke-PythonCommand "-m pip install --upgrade pip"
Invoke-PythonCommand "-m pip install pyinstaller"
Invoke-PythonCommand "-m pip install -r player/requirements.txt"
Write-Host "Dependencies ready." -ForegroundColor Green

# 4. Build Updater
Write-Host "[4/7] Packaging Updater..." -ForegroundColor Yellow
Push-Location player
try {
    Invoke-PythonCommand "-m PyInstaller --noconfirm --clean --onefile --windowed --noupx --name Updater updater/main.py"
    if (-not (Test-Path "dist/Updater.exe")) {
        Write-Error "Updater compilation failed."
    }
    Copy-Item -Path "dist/Updater.exe" -Destination "." -Force
    Write-Host "Updater.exe built and placed in player/ folder." -ForegroundColor Green
} finally {
    Pop-Location
}

# 5. Build Simple Audio Player
Write-Host "[5/7] Packaging Main Application..." -ForegroundColor Yellow
Push-Location player
try {
    # Set PYTHONPATH
    $env:PYTHONPATH = "$((Get-Location).Path);$((Get-Location).Parent.Path)"
    Invoke-PythonCommand "-m PyInstaller --noconfirm SimpleAudioPlayer.spec"
    if (-not (Test-Path "dist/SimpleAudioPlayer/SimpleAudioPlayer.exe")) {
        Write-Error "Main application packaging failed."
    }
    Write-Host "Application package created under player/dist/SimpleAudioPlayer/." -ForegroundColor Green
} finally {
    Pop-Location
}

# 6. Apply modified winsdk binary naming patch
Write-Host "[6/7] Applying WinRT binary patch..." -ForegroundColor Yellow
if (Test-Path "winsdk/_winrt.pyd") {
    Copy-Item -Path "winsdk/_winrt.pyd" -Destination "player/dist/SimpleAudioPlayer/_winrt.pyd" -Force
    if (Test-Path "player/dist/SimpleAudioPlayer/winsdk_winrt.pyd") {
        Remove-Item -Path "player/dist/SimpleAudioPlayer/winsdk_winrt.pyd" -Force
    }
    Write-Host "WinRT binary patch applied successfully (_winrt.pyd copied, winsdk_winrt.pyd removed)." -ForegroundColor Green
} else {
    Write-Warning "winsdk/_winrt.pyd not found. Skipping patch. The build may crash on media controls."
}

# 7. Build Installer using Inno Setup
Write-Host "[7/7] Compiling Installer (Inno Setup)..." -ForegroundColor Yellow
$iscc = "iscc"
if (-not (Get-Command "iscc" -ErrorAction SilentlyContinue)) {
    $common_paths = @(
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        "C:\Program Files\Inno Setup 6\ISCC.exe",
        "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    )
    foreach ($path in $common_paths) {
        if (Test-Path $path) {
            $iscc = $path
            break
        }
    }
}

if ($iscc -eq "iscc" -and -not (Get-Command "iscc" -ErrorAction SilentlyContinue)) {
    Write-Warning "Inno Setup compiler (ISCC.exe) was not found. Please install Inno Setup 6 and add it to PATH."
    Write-Host "Skipping installer compilation step." -ForegroundColor Yellow
} else {
    Write-Host "Using ISCC path: $iscc" -ForegroundColor Gray
    & $iscc player/simple_audio_player.iss
    
    # Rename and bundle assets
    if (Test-Path "player/dist/SimpleAudioPlayerSetup.exe") {
        Move-Item -Path "player/dist/SimpleAudioPlayerSetup.exe" -Destination "player/dist/SimpleAudioPlayer-v$VERSION.exe" -Force
        Compress-Archive -Path "player/dist/SimpleAudioPlayer/*" -DestinationPath "player/dist/SimpleAudioPlayer-v$VERSION.zip" -Force
        
        Write-Host "=============================================" -ForegroundColor Green
        Write-Host "Build successful!" -ForegroundColor Green
        Write-Host "Installer: player/dist/SimpleAudioPlayer-v$VERSION.exe" -ForegroundColor Green
        Write-Host "ZIP Archive: player/dist/SimpleAudioPlayer-v$VERSION.zip" -ForegroundColor Green
        Write-Host "=============================================" -ForegroundColor Green
    } else {
        Write-Error "Installer compilation did not produce SimpleAudioPlayerSetup.exe."
    }
}
