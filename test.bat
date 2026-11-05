@echo off
cd /d "%~dp0"
title CivicTrack-AI - Test Suite
echo Running CivicTrack-AI Test Suite...
"C:\Users\ADMIN\AppData\Local\Python\pythoncore-3.14-64\python.exe" test_app.py
pause
