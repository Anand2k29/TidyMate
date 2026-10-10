@echo off
title Install the start_here command
cd /d "%~dp0"

py -3 --version >nul 2>nul
if %errorlevel%==0 (
    py -3 -m tidymate setup
    goto end
)
python --version >nul 2>nul
if %errorlevel%==0 (
    python -m tidymate setup
    goto end
)

echo.
echo  Python was not found on this computer.
echo.
echo   1. Go to https://www.python.org/downloads/
echo   2. Download and install it - tick "Add Python to PATH" on the first screen
echo   3. Double-click this file again
echo.
echo  (If Windows opened the Microsoft Store, close it and use python.org instead.)
echo.

:end
echo.
pause
