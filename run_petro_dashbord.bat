@echo off
title Django Development Server - 192.168.17.168:8000
cd /d "%~dp0"

echo Starting Django server on 192.168.17.168:8000...
echo Make sure you are in the correct project directory.
echo.

:run
python manage.py runserver 192.168.17.168:8000
echo.
echo [%date% %time%] Server stopped or crashed.
echo Restarting in 5 seconds... (Press Ctrl+C to stop)
timeout /t 5 /nobreak >nul
echo.
goto run