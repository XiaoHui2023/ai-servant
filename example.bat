@echo off
setlocal EnableExtensions
cd /d "%~dp0"
python example\__main__.py
exit /b %ERRORLEVEL%
