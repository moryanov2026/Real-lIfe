@echo off
REM Pravi lipsvashtite vremenni kartinki i obnovyava spisaka KARTINKI.html (koe e narisuvano).
cd /d "%~dp0"
set PY=
py -3.12 --version >nul 2>&1 && set PY=py -3.12
if "%PY%"=="" py -3 --version >nul 2>&1 && set PY=py -3
if "%PY%"=="" set PY=python
%PY% tools\art.py
start "" KARTINKI.html
pause
