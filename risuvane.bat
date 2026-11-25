@echo off
REM Risuva baba Stana s programata v tools\pixelart i zapisva kartinkite v igrata.
cd /d "%~dp0"
set PY=
py -3.12 --version >nul 2>&1 && set PY=py -3.12
if "%PY%"=="" py -3 --version >nul 2>&1 && set PY=py -3
if "%PY%"=="" set PY=python
%PY% tools\pixelart\make_baba.py
start "" art_src\baba_stana_preview.png
pause
