@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call "%~dp0update.bat"
set "PYTHONPATH=%~dp0src"
".venv\Scripts\python.exe" -m unittest discover -s tests -v
