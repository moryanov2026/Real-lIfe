@echo off
REM Startira igrata Real Life. "start.bat fps" pokazva kadrite v sekunda.
cd /d "%~dp0"
set PY=
py -3.12 --version >nul 2>&1 && set PY=py -3.12
if "%PY%"=="" py -3 --version >nul 2>&1 && set PY=py -3
if "%PY%"=="" set PY=python
if "%1"=="fps" (%PY% main.py --fps) else (%PY% main.py)
if errorlevel 1 pause
