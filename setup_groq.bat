@echo off
REM Quick Groq Setup Script
echo ============================================================
echo   GROQ AI SETUP - Free & Fast Script Generation
echo ============================================================
echo.
echo This script will help you set up Groq for your YouTube Shorts generator.
echo.
echo Step 1: Get your FREE API key
echo   Visit: https://console.groq.com
echo   Sign up (takes 1 minute)
echo   Create an API Key
echo.
pause
echo.
echo Step 2: Enter your Groq API key below
echo.
set /p GROQ_KEY="Paste your Groq API key (starts with gsk_): "
echo.

REM Create or update .env file
if exist .env (
    echo Updating existing .env file...
    
    REM Check if GROQ_API_KEY already exists
    findstr /C:"GROQ_API_KEY" .env >nul
    if %errorlevel%==0 (
        REM Replace existing key
        powershell -Command "(gc .env) -replace 'GROQ_API_KEY=.*', 'GROQ_API_KEY=%GROQ_KEY%' | Out-File -encoding ASCII .env"
    ) else (
        REM Add new key
        echo GROQ_API_KEY=%GROQ_KEY% >> .env
    )
    
    REM Ensure AI_PROVIDER is set to groq
    findstr /C:"AI_PROVIDER" .env >nul
    if %errorlevel%==0 (
        powershell -Command "(gc .env) -replace 'AI_PROVIDER=.*', 'AI_PROVIDER=groq' | Out-File -encoding ASCII .env"
    ) else (
        echo AI_PROVIDER=groq >> .env
    )
) else (
    echo Creating new .env file...
    echo # YouTube Shorts Maker - Environment Variables > .env
    echo. >> .env
    echo # AI Provider Configuration >> .env
    echo AI_PROVIDER=groq >> .env
    echo GROQ_API_KEY=%GROQ_KEY% >> .env
)

echo.
echo ============================================================
echo   SUCCESS! Groq is now configured!
echo ============================================================
echo.
echo Your settings:
echo   - AI Provider: Groq (Free & Fast)
echo   - API Key: %GROQ_KEY:~0,20%...
echo.
echo Testing connection...
echo.
python utils/ai_providers.py
echo.
echo ============================================================
echo.
echo You're all set! Run your video generator:
echo   python start_app.py
echo.
echo Or generate multiple videos:
echo   python generate_5_videos.py
echo.
echo ============================================================
pause

