@echo off
REM Reinstall all packages in virtual environment

echo.
echo ============================================================
echo REINSTALLING PACKAGES IN VIRTUAL ENVIRONMENT
echo ============================================================
echo.

REM Navigate to project folder
D:
cd D:\YouTubeShortsProject\NCWM

REM Activate virtual environment
echo Activating virtual environment...
call D:\YouTubeShortsProject\python_env\Scripts\activate

REM Install packages
echo Installing packages...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Test installation
echo.
echo Testing installation...
python -c "import moviepy.editor; print('✓ MoviePy installed')"
python -c "import customtkinter; print('✓ CustomTkinter installed')"
python -c "import ollama; print('✓ Ollama installed')"
python -c "import torch; print('✓ PyTorch installed')"
python -c "import diffusers; print('✓ Diffusers installed')"

echo.
echo ============================================================
echo PACKAGE REINSTALLATION COMPLETE
echo ============================================================
echo.
echo You can now run: launch_app.bat
echo.

pause

