@echo off
REM Quick Configuration Switcher
REM Easily switch between different optimization presets

echo.
echo ============================================================
echo YOUTUBE SHORTS MAKER - CONFIGURATION SWITCHER
echo ============================================================
echo.
echo Select your desired mode:
echo.
echo 1. ULTRA FAST   (60-80 seconds, 720p, 2 scenes)
echo 2. BALANCED     (2-3 minutes, 1080p, 3 scenes) [CURRENT]
echo 3. PRODUCTION   (4-5 minutes, 1080p, best quality)
echo 4. Cancel
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" goto ultrafast
if "%choice%"=="2" goto balanced
if "%choice%"=="3" goto production
if "%choice%"=="4" goto cancel

:ultrafast
echo.
echo Activating ULTRA FAST mode...
copy /Y config_ultra_fast.py settings\config.py
echo.
echo [SUCCESS] ULTRA FAST mode activated!
echo.
echo What changed:
echo   - Resolution: 720p (faster rendering)
echo   - FPS: 20 (faster encoding)
echo   - AI Steps: 8 (minimum for quality)
echo   - AI Model: phi3 (faster)
echo.
echo Expected time: 60-80 seconds per video
echo.
echo MANUAL STEP REQUIRED:
echo Edit steps\step3_generate_backgrounds.py line 68
echo Change: optimized_scenes = scene_descriptions[:3]
echo To:     optimized_scenes = scene_descriptions[:2]
echo.
pause
goto end

:balanced
echo.
echo Activating BALANCED mode (current default)...
echo This is already your active configuration.
echo.
echo Settings:
echo   - Resolution: 1080p
echo   - FPS: 24
echo   - AI Steps: 15
echo   - Scenes: 3
echo.
echo Expected time: 2-3 minutes per video
echo.
pause
goto end

:production
echo.
echo Activating PRODUCTION mode...
copy /Y config_production.py settings\config.py
echo.
echo [SUCCESS] PRODUCTION mode activated!
echo.
echo What changed:
echo   - Resolution: 1080p (full quality)
echo   - FPS: 30 (smoother)
echo   - AI Steps: 25 (best quality)
echo   - Quality: Production preset
echo.
echo Expected time: 4-5 minutes per video
echo.
echo MANUAL STEP REQUIRED:
echo Edit steps\step3_generate_backgrounds.py line 68
echo Change: optimized_scenes = scene_descriptions[:3]
echo To:     optimized_scenes = scene_descriptions[:4]
echo (This gives you 4 scenes for more variety)
echo.
pause
goto end

:cancel
echo.
echo Cancelled. No changes made.
echo.
pause
goto end

:end




