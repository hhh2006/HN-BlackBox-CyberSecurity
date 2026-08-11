@echo off
title HN BlackBox
cd /d "%~dp0"
python main.py
if errorlevel 1 pause
