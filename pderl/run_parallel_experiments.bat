@echo off
chcp 65001 >nul
echo ========================================
echo PDERL 并行训练启动脚本
echo ========================================
echo.

:: 检查是否在正确的conda环境中
if "%CONDA_DEFAULT_ENV%" neq "erl_env" (
    echo ⚠️ 警告: 当前不在 erl_env 环境中
    echo 💡 请先运行: conda activate erl_env
    echo.
    pause
    exit /b 1
)

echo ✅ 当前环境: %CONDA_DEFAULT_ENV%
echo.

:: 显示可用的预设配置
echo 📋 可用的预设配置:
echo   1. quick_test    - 快速测试 (3个种子, 较少训练步数)
echo   2. standard      - 标准实验 (5个种子)
echo   3. comprehensive - 全面实验 (10个种子)
echo   4. custom_seeds  - 自定义种子 (5个特定种子)
echo.

:: 选择环境
echo 🎮 请选择训练环境:
echo   1. Hopper-v2
echo   2. Walker2d-v2
echo   3. HalfCheetah-v2
echo   4. Ant-v2
echo   5. Swimmer-v2
echo   6. Reacher-v2
echo.
set /p env_choice=请输入环境编号 (1-6): 

if "%env_choice%"=="1" set env_name=Hopper-v2
if "%env_choice%"=="2" set env_name=Walker2d-v2
if "%env_choice%"=="3" set env_name=HalfCheetah-v2
if "%env_choice%"=="4" set env_name=Ant-v2
if "%env_choice%"=="5" set env_name=Swimmer-v2
if "%env_choice%"=="6" set env_name=Reacher-v2

if "%env_name%"=="" (
    echo ❌ 无效的环境选择
    pause
    exit /b 1
)

echo ✅ 选择的环境: %env_name%
echo.

:: 选择预设
set /p preset_choice=请输入预设编号 (1-4): 

if "%preset_choice%"=="1" set preset_name=quick_test
if "%preset_choice%"=="2" set preset_name=standard
if "%preset_choice%"=="3" set preset_name=comprehensive
if "%preset_choice%"=="4" set preset_name=custom_seeds

if "%preset_name%"=="" (
    echo ❌ 无效的预设选择
    pause
    exit /b 1
)

echo ✅ 选择的预设: %preset_name%
echo.

:: 询问是否使用CUDA
set /p use_cuda=是否使用CUDA加速? (y/n, 默认n): 
if "%use_cuda%"=="" set use_cuda=n

:: 构建命令
set cmd=python parallel_train.py -env %env_name% -preset %preset_name%

if /i "%use_cuda%"=="y" (
    set cmd=%cmd% -use_cuda
    echo ✅ 启用CUDA加速
)

echo.
echo 🚀 即将执行的命令:
echo %cmd%
echo.
set /p confirm=确认开始训练? (y/n): 

if /i "%confirm%" neq "y" (
    echo ❌ 已取消
    pause
    exit /b 0
)

echo.
echo 🎯 开始并行训练...
echo ========================================

:: 执行训练
%cmd%

echo.
echo ========================================
echo 🏁 训练完成!
echo 📁 结果保存在: parallel_experiments 目录
echo.
pause