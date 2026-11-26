@echo off
REM Pravi RealLife.exe za uchenicite - na tyah NE im tryabva Python.
REM Pusni s dvoen klik. Na kraya ima RealLife.zip - tova se dava na uchenicite.
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   Real Life - BUILD (RealLife.exe)
echo ============================================
echo.
set PY=
py -3.12 --version >nul 2>&1 && set PY=py -3.12
if "%PY%"=="" py -3 --version >nul 2>&1 && set PY=py -3
if "%PY%"=="" set PY=python

echo 1) Instaliram PyInstaller...
%PY% -m pip install --upgrade pyinstaller
if errorlevel 1 (
  echo GRESHKA: PyInstaller ne se instalira. Pusni purvo install.bat.
  pause
  exit /b 1
)

echo.
echo 2) Sglobyavam igrata ^(1-2 minuti^)...
if exist build rmdir /s /q build
if exist dist\RealLife rmdir /s /q dist\RealLife
%PY% -m PyInstaller --noconfirm --clean --windowed --name RealLife main.py
if errorlevel 1 (
  echo GRESHKA pri sglobyavaneto. Snimai ekrana i mi go pokazhi.
  pause
  exit /b 1
)

echo.
echo 3) Kopiram kartinkite, kartite, pesnite...
xcopy /e /i /q /y data dist\RealLife\data >nul
xcopy /e /i /q /y assets dist\RealLife\assets >nul
copy /y PROCHETI.txt dist\RealLife\ >nul

echo.
echo 4) Proverka na gotovata igra...
if exist dist\RealLife\selftest.txt del dist\RealLife\selftest.txt
start "" /wait dist\RealLife\RealLife.exe --selftest
type dist\RealLife\selftest.txt
findstr /b "OK" dist\RealLife\selftest.txt >nul
if errorlevel 1 (
  echo.
  echo Proverkata NE mina. Snimai ekrana i mi go pokazhi.
  pause
  exit /b 1
)
del dist\RealLife\selftest.txt

echo.
echo 5) Pravya RealLife.zip...
if exist RealLife.zip del RealLife.zip
powershell -NoProfile -Command "Compress-Archive -Path 'dist\RealLife' -DestinationPath 'RealLife.zip' -Force"

echo.
echo ============================================
echo   GOTOVO!  RealLife.zip e v papkata na igrata.
echo   Kopirai go na uchenicite: razarhivirat i pusnat RealLife.exe
echo ============================================
pause
