@echo off
cd /d "%~dp0"
where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw -3 "%~dp0app.py" %*
    exit /b
)
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%~dp0app.py" %*
    exit /b
)
if exist "D:\python\pythonw.exe" (
    start "" "D:\python\pythonw.exe" "%~dp0app.py" %*
    exit /b
)
echo Python was not found. Install Python 3 and requirements.txt dependencies.
pause
