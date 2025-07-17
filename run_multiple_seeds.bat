@echo off
setlocal enabledelayedexpansion
REM ========================================
REM ERL Multi-Seed Parallel Training Script
REM ========================================

REM Configuration variables - modify these as needed
set ENV_NAME=HalfCheetah-v2
set CONDA_ENV=erl_env
set PYTHON_SCRIPT=run_erl.py

REM Define seeds to use (space separated)
set SEEDS=1 2 3 5 42

REM Optional: Set startup delay (seconds) to avoid resource conflicts
set START_DELAY=3

REM ========================================
REM Display configuration information
REM ========================================
echo ========================================
echo ERL Multi-Seed Parallel Training Launcher
echo ========================================
echo Environment: %ENV_NAME%
echo Conda Environment: %CONDA_ENV%
echo Python Script: %PYTHON_SCRIPT%
echo Seeds: %SEEDS%
echo Startup Delay: %START_DELAY% seconds
echo ========================================
echo.

REM Confirm before proceeding
set /p confirm="Confirm to start all experiments? (y/n): "
if /i not "%confirm%"=="y" (
    echo Startup cancelled
    pause
    exit /b
)

echo Starting experiments...
echo.

REM ========================================
REM Experiment startup loop
REM ========================================
set count=0
for %%s in (%SEEDS%) do (
    set /a count+=1
    echo [!count!] Starting experiment with Seed %%s...
    start "ERL_%ENV_NAME%_seed_%%s" cmd /k "conda activate %CONDA_ENV% && python %PYTHON_SCRIPT% -env %ENV_NAME% -seed %%s"
    
    REM Add startup delay (except for the last one)
    if !count! lss 5 (
        echo    Waiting %START_DELAY% seconds before starting next experiment...
        timeout /t %START_DELAY% /nobreak >nul
    )
)

echo.
echo ========================================
echo All experiments have been started!
echo Total experiments launched: %count%
echo ========================================
echo.
echo Tips:
echo - Each experiment runs in a separate command window
echo - You can identify different experiments by window title
echo - Results will be saved in respective directories
echo - Use nvidia-smi to monitor GPU usage
echo.
pause