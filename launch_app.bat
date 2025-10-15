@echo off
REM YouTube Shorts Maker - Optimized Launcher
REM This activates the D drive virtual environment correctly with memory optimizations

echo.
echo ============================================================
echo LAUNCHING YOUTUBE SHORTS MAKER (OPTIMIZED)
echo ============================================================
echo.

REM OPTIMIZATION: Check for existing Python processes
echo Checking for existing Python processes...
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo WARNING: Python processes detected. Consider closing them for optimal memory usage.
    echo Press Ctrl+C to cancel and close other Python processes, or press any key to continue...
    pause >nul
)

REM Navigate to D drive and project
D:
cd D:\YouTubeShortsProject\NCWM

REM OPTIMIZATION: Set memory efficiency environment variables
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

REM OPTIMIZATION: Quick memory check
echo Checking system memory...
python -c "try: import psutil; mem=psutil.virtual_memory(); print(f'Memory: {mem.available/(1024**3):.1f} GB available'); print('Memory check complete')" 2>nul || echo "Memory check skipped (psutil not available)"

REM Run the app
echo Starting YouTube Shorts Maker...
python start_app.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Application crashed
    echo ============================================================
    echo.
    echo Try these solutions:
    echo   1. Run: reinstall_packages.bat
    echo   2. Close other applications to free memory
    echo   3. Restart your computer if memory is very low
    echo   4. Check Task Manager for stuck Python processes
    echo.
    pause
)

