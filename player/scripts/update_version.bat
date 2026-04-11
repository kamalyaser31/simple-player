@echo off
set /p version="Enter new version (e.g. 1.3.0): "
if "%version%"=="" (
    echo Version cannot be empty.
    pause
    exit /b 1
)
python "%~dp0update_version.py" %version%
pause
