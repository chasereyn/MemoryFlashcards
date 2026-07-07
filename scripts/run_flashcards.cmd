@echo off
cd /d "%~dp0\.."
REM cmd /k keeps the window open after exit or Ctrl+C
cmd /k python main.py
