@echo off
REM Otvarya redaktora na karti. "editor.bat data\maps\kashta.json" otvarya druga karta.
cd /d "%~dp0"
set PY=
py -3.12 --version >nul 2>&1 && set PY=py -3.12
if "%PY%"=="" py -3 --version >nul 2>&1 && set PY=py -3
if "%PY%"=="" set PY=python
%PY% editor.py %1
if errorlevel 1 pause
