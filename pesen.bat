@echo off
REM Pravi pesen za minigrata "Svirene" ot zapis (mp3, wav, ogg, m4a).
REM NAI-LESNO: vlachi mp3 faila VARHU tozi fail (pesen.bat). Ili go pusni s dvoen klik i izberi faila.
REM Programata pita za ime na pesenta i za instrumenta (kaval), sled tova slaga pesenta v igrata.
chcp 65001 >nul
cd /d "%~dp0"
set PY=
py -3.12 --version >nul 2>&1 && set PY=py -3.12
if "%PY%"=="" py -3 --version >nul 2>&1 && set PY=py -3
if "%PY%"=="" set PY=python
if "%~1"=="" (
  %PY% tools\muzika_v_pesen.py
) else (
  %PY% tools\muzika_v_pesen.py "%~1"
)
pause
