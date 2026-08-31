@echo off
setlocal
cd /d "%~dp0"
call build.bat
if errorlevel 1 exit /b 1
set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
  echo Inno Setup 6 is not installed.
  exit /b 1
)
"%ISCC%" installer.iss
