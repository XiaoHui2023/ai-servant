@echo off
setlocal EnableExtensions
rem Pack ai-servant as a PyInstaller onefile executable.
rem Usage: tools\pack.bat [src]
rem Outputs: dist\ai-servant.exe and dist\ai-servant-<version>-windows.zip.
rem Windows builds do not run staticx.
cd /d "%~dp0\.."

set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=src"
if /I not "%TARGET%"=="src" (
    echo usage: tools\pack.bat [src] >&2
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv 2>nul || python -m venv .venv
    if errorlevel 1 exit /b 1
)

set "PY=%CD%\.venv\Scripts\python.exe"
"%PY%" -V
if errorlevel 1 exit /b 1
"%PY%" -m pip install -q -U pip setuptools wheel
if errorlevel 1 exit /b 1
"%PY%" -m pip install -q --upgrade --force-reinstall -e .
if errorlevel 1 exit /b 1
"%PY%" -m pip install -q --upgrade --force-reinstall "pyinstaller>=6.0"
if errorlevel 1 exit /b 1

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

"%PY%" -m PyInstaller --clean --noconfirm "%CD%\ai-servant-cli.spec"
if errorlevel 1 exit /b 1
if not exist "%CD%\dist\ai-servant.exe" (
    echo error: dist\ai-servant.exe was not created >&2
    exit /b 1
)

"%PY%" tools\bundle_release.py
if errorlevel 1 exit /b 1

echo PyInstaller output: %CD%\dist
exit /b 0
