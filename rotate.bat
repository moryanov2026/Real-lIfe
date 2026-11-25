@echo off
REM Zavartva mebel na 90 gradusa. Primer:  rotate.bat table      (vzema assets\table.png)
REM Rezultat: drafts\table_right.png i drafts\table_preview.png
cd /d "%~dp0"
set PY=
py -3.12 --version >nul 2>&1 && set PY=py -3.12
if "%PY%"=="" py -3 --version >nul 2>&1 && set PY=py -3
if "%PY%"=="" set PY=python
if "%2"=="" (%PY% tools\rotate.py assets\%1.png) else (%PY% tools\rotate.py assets\%1.png --legs %2)
pause
