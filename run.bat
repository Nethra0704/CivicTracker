@echo off
cd /d "%~dp0"
title CivicTrack-AI - Flask Server
echo ========================================================
echo  CivicTrack-AI - Starting Flask Web Server
echo  Access at: http://127.0.0.1:5000
echo ========================================================
"C:\Users\ADMIN\AppData\Local\Python\pythoncore-3.14-64\python.exe" app.py
pause
