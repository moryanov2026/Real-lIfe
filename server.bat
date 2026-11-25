@echo off
REM Puska samo SARVARA (bez prozorec na igrata). Uchenicite vlizat s adresa, koito se pokazva.
REM Pri parvo puskane Windows pita za zashtitnata stena: natisni "Allow access" / "Razreshi".
cd /d "%~dp0"
set PY=
py -3.12 --version >nul 2>&1 && set PY=py -3.12
if "%PY%"=="" py -3 --version >nul 2>&1 && set PY=py -3
if "%PY%"=="" set PY=python
%PY% server.py
pause
