@echo off
REM LAUNCH STABLE DIFFUSION WEBUI WITH API ENABLED
REM This script starts the AUTOMATIC1111 WebUI for YouTube Shorts generation

echo.
echo ================================================================
echo  LAUNCHING STABLE DIFFUSION WEBUI WITH API
echo ================================================================
echo.

cd /d "%~dp0stable-diffusion-webui"

if not exist "webui-user.bat" (
    echo ERROR: stable-diffusion-webui not found!
    echo Please run: git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
    echo.
    pause
    exit /b 1
)

echo Starting WebUI with API enabled...
echo.
echo The WebUI will be available at: http://127.0.0.1:7860
echo API endpoint: http://127.0.0.1:7860/docs
echo.
echo Press Ctrl+C to stop the WebUI
echo.

REM Launch WebUI with API flag and optimizations for RTX 2060 (6GB)
set COMMANDLINE_ARGS=--api --medvram --opt-sdp-attention --no-half-vae

call webui-user.bat

pause

