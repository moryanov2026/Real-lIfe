@echo off
REM Install za igrata Real Life (Windows). Puska se s dvoen klik.
REM Pishem na latinica, za da se vizhda pravilno v cherniya prozorec.
cd /d "%~dp0"
echo ============================================
echo   Real Life - instalaciya
echo ============================================
echo.

REM 1) Tarsim Python (komanda "py" ili "python")
set PY=
py -3.12 --version >nul 2>&1 && set PY=py -3.12
if "%PY%"=="" py -3 --version >nul 2>&1 && set PY=py -3
if "%PY%"=="" (
  python --version >nul 2>&1 && set PY=python
)

REM 2) Ako nyama Python, opitvame da go instalirame s winget (Windows 10/11)
if "%PY%"=="" (
  echo Python ne e nameren. Opitvam da go instaliram...
  winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
  echo.
  echo Ako instalaciyata pravilno svarshi, ZATVORI tozi prozorec i pusni install.bat OTNOVO.
  echo Ako winget ne rabota, svali Python ot https://www.python.org/downloads/
  echo i pri instalaciya markirai "Add python.exe to PATH".
  pause
  exit /b 1
)

echo Nameren Python:
%PY% --version
echo.

REM 3) Instaliram Pygame. Za nov Python (napr. 3.14) oficialniyat "pygame" nyama gotov paket,
REM zatova purvo probvame "pygame-ce" (sashtiyat import, sashtata igra), samo gotovi paketi.
echo Instaliram Pygame...
%PY% -m pip install --only-binary :all: pygame-ce
if errorlevel 1 (
  echo pygame-ce ne stana, probvam obiknovenia pygame...
  %PY% -m pip install --only-binary :all: pygame
)
if errorlevel 1 (
  echo.
  echo GRESHKA: nyama gotov Pygame za tazi versiya na Python.
  echo Reshenie: instaliram Python 3.12 do tekushtiya ^(ne maha nishto^)...
  winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
  echo Zatvori tozi prozorec i pusni install.bat OTNOVO.
  pause
  exit /b 1
)

REM 4) Proverka dali vsichko raboti (test bez prozorec)
echo.
echo Pravya proverka...
%PY% test_game.py
if errorlevel 1 (
  echo.
  echo Proverkata ne mina. Snimai ekrana i mi go pokazhi.
  pause
  exit /b 1
)

echo.
echo ============================================
echo   GOTOVO! Za da igraesh, pusni start.bat
echo ============================================
pause
