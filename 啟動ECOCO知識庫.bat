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

:: 2. Install dependencies (including google-generativeai for AI client service)
echo [2] Installing dependencies...
%PY_CMD% -m pip install fastapi uvicorn pydantic psycopg2-binary google-generativeai --quiet
if %errorlevel% neq 0 (
    echo [!] Install failed, trying to start anyway...
)

:: 3. Kill any existing process on port 7777
echo [3] Checking port 7777...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7777 ^| findstr LISTENING') do (
    echo [!] Port 7777 in use by PID %%a, terminating...
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 >nul

:: 4. Start server and auto-open browser
echo [4] Starting Server (PORT 7777)...
echo Please leave this window open.
echo.
echo ==========================================
echo   http://127.0.0.1:7777
echo ==========================================
echo.

:: Open browser after 3 seconds
start /b cmd /c "timeout /t 3 >nul && start "" http://127.0.0.1:7777/"

:: Execute server
%PY_CMD% faq_server.py --host 127.0.0.1 --port 7777

if %errorlevel% neq 0 (
    echo.
    echo [CRASH] Code: %errorlevel%
)
pause
