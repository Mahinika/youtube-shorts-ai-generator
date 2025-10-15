@echo off
REM YouTube Shorts Maker - Console Visible Launcher
REM This keeps the console window open to show progress

echo.
echo ============================================================
echo LAUNCHING YOUTUBE SHORTS MAKER (CONSOLE VISIBLE)
echo ============================================================
echo.

REM Navigate to D drive and project
D:
cd D:\YouTubeShortsProject\NCWM

REM Set memory optimization environment variables
echo Setting memory optimization environment variables...
set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
set OMP_NUM_THREADS=4
set MKL_NUM_THREADS=4

REM Activate the virtual environment
echo Activating virtual environment...
call D:\YouTubeShortsProject\python_env\Scripts\activate

REM Confirm activation
echo Virtual environment activated successfully
python -c "import sys; print(f'Python: {sys.executable}')"
echo.

REM Check GPU status
echo Checking GPU status...
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
echo.

REM Run the app with console output
echo Starting YouTube Shorts Maker...
echo NOTE: Keep this window open to see generation progress!
echo.
python start_app.py

REM Keep window open
echo.
echo ============================================================
echo Application finished
echo ============================================================
echo.
pause
