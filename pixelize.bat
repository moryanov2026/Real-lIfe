@echo off
REM Obrabotva surovi kartinki ot papka raw_art i gi slaga v assets.
REM Primer:  pixelize.bat hero 10     (preset hero, do 10 tsvyata)
REM Presets: hero wall door window tile floor object icon table_big bed item building_s building_m building_l tileset
cd /d "%~dp0"
set PY=
py -3.12 --version >nul 2>&1 && set PY=py -3.12
if "%PY%"=="" py -3 --version >nul 2>&1 && set PY=py -3
if "%PY%"=="" set PY=python
set PRESET=%1
if "%PRESET%"=="" set PRESET=hero
set COLORS=%2
if "%COLORS%"=="" set COLORS=10
%PY% tools\pixelize.py raw_art --preset %PRESET% --colors %COLORS% --out assets
pause
