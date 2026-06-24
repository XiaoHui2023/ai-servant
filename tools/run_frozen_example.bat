@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
set "AI_SERVANT_EXE=%CD%\dist\ai-servant.exe"
python example\__main__.py
exit /b %ERRORLEVEL%
