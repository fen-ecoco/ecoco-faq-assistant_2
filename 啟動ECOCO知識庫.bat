@echo off
title ECOCO FAQ Launcher
echo ==========================================
echo   ECOCO FAQ Assistant Startup Tool
echo ==========================================
echo.

:: Get current directory
cd /d "%~dp0"

:: 1. Check Python
echo [1] Checking Python...
set PY_CMD=python

:: Try standard command
python --version >nul 2>&1
if %errorlevel% neq 0 (
    set PY_CMD=py
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        set PY_CMD="C:\Users\fen\AppData\Local\Microsoft\WindowsApps\python.exe"
        %PY_CMD% --version >nul 2>&1
        if %errorlevel% neq 0 (
            echo [ERROR] Python not found.
            pause
            exit /b
        )
    )
)
echo Using: %PY_CMD%

:: 2. Install
echo [2] Installing dependencies...
%PY_CMD% -m pip install fastapi uvicorn pydantic
if %errorlevel% neq 0 (
    echo [!] Install failed, trying to start anyway...
)

:: 3. Start
echo [3] Starting Server (PORT 7777)...
echo Please leave this window open.

:: Open browser
start /b cmd /c "timeout /t 3 >nul && start "" http://127.0.0.1:7777/"

:: Execute
%PY_CMD% faq_server.py --host 127.0.0.1 --port 7777

if %errorlevel% neq 0 (
    echo.
    echo [CRASH] Code: %errorlevel%
)
pause
