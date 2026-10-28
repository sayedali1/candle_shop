@echo off
rem Double-click this file to open the candle page.
rem The 3D candle cannot run when index.html is opened directly, so this starts a tiny local server first.
cd /d "%~dp0"
echo Starting the page at http://localhost:8000  (close this window to stop it)
start "" http://localhost:8000
python serve.py 8000 || py serve.py 8000
pause
