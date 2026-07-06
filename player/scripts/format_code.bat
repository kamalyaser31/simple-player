@echo off
setlocal
cd /d "%~dp0\.."
py scripts\format_code.py %*
pause
endlocal
