@echo off
REM MODEL DOWNLOADER - Batch Script
REM Downloads Stable Diffusion model to avoid waiting during generation

echo.
echo ============================================================
echo STABLE DIFFUSION MODEL DOWNLOADER
echo ============================================================
echo.

REM Navigate to project
D:
cd D:\YouTubeShortsProject\NCWM

REM Activate virtual environment
echo Activating virtual environment...
call D:\YouTubeShortsProject\python_env\Scripts\activate

REM Set memory optimization environment variables
set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
set OMP_NUM_THREADS=4
set MKL_NUM_THREADS=4

REM Run the downloader
echo.
echo Starting model download...
echo This will take 10-15 minutes but only needs to be done once!
echo.
python download_model.py

REM Keep window open
echo.
pause



