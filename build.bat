@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m PyInstaller --noconfirm --clean DuoPlayer.spec
) else (
    python -m PyInstaller --noconfirm --clean DuoPlayer.spec
)
if errorlevel 1 exit /b 1
del /q "dist\DuoPlayer\_internal\icuuc.dll" 2>nul
del /q "dist\DuoPlayer\_internal\icudt*.dll" 2>nul
if not exist "dist\DuoPlayer\mpv" mkdir "dist\DuoPlayer\mpv"
copy /y "C:\Program Files\MPV Player\mpv.exe" "dist\DuoPlayer\mpv\mpv.exe" >nul
if exist "C:\Program Files\MPV Player\d3dcompiler_43.dll" copy /y "C:\Program Files\MPV Player\d3dcompiler_43.dll" "dist\DuoPlayer\mpv\d3dcompiler_43.dll" >nul
echo Build complete: %~dp0dist\DuoPlayer\DuoPlayer.exe
