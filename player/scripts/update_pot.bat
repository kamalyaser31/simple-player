@echo off
setlocal
cd /d "%~dp0\.."
py scripts\update_pot.py %*
endlocal
