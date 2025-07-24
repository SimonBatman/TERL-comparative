#!/bin/bash

# 设置UTF-8编码
export LANG=en_US.UTF-8

echo "========================================"
echo "PDERL 并行训练启动脚本 (Linux版)"
echo "========================================"
echo

# 检查是否在正确的conda环境中
if [ "$CONDA_DEFAULT_ENV" != "erl_env" ]; then
    echo "⚠️ 警告: 当前不在 erl_env 环境中"
    echo "💡 请先运行: conda activate erl_env"
    echo
    exit 1
fi

echo "✅ 当前环境: $CONDA_DEFAULT_ENV"
echo

# 显示可用的预设配置
echo "📋 可用的预设配置:"
echo "  1. quick_test    - 快速测试 (3个种子, 较少训练步数)"
echo "  2. standard      - 标准实验 (5个种子)"
echo "  3. comprehensive - 全面实验 (10个种子)"
echo "  4. custom_seeds  - 自定义种子 (5个特定种子)"
echo "  5. gpu_optimized - GPU优化 (5个种子, 适合16G显存, 启用TensorBoard)"
echo "  6. custom        - 自定义配置"
echo

# 选择环境
echo "🎮 请选择训练环境:"
echo "  1. Hopper-v2"
echo "  2. Walker2d-v2"
echo "  3. HalfCheetah-v2"
echo "  4. Ant-v2"
echo "  5. Swimmer-v2"
echo "  6. Reacher-v2"
echo
read -p "请输入环境编号 (1-6): " env_choice

case $env_choice in
    1) env_name="Hopper-v2" ;;
    2) env_name="Walker2d-v2" ;;
    3) env_name="HalfCheetah-v2" ;;
    4) env_name="Ant-v2" ;;
    5) env_name="Swimmer-v2" ;;
    6) env_name="Reacher-v2" ;;
    *) echo "❌ 无效的环境选择"; exit 1 ;;
esac

echo "✅ 选择的环境: $env_name"
echo

# 选择预设
read -p "请输入预设编号 (1-5): " preset_choice

case $preset_choice in
    1) preset_name="quick_test" ;;
    2) preset_name="standard" ;;
    3) preset_name="comprehensive" ;;
    4) preset_name="custom_seeds" ;;
    5) preset_name="gpu_optimized" ;;
    *) echo "❌ 无效的预设选择"; exit 1 ;;
esac

echo "✅ 选择的预设: $preset_name"
echo

# 询问是否使用CUDA
read -p "是否使用CUDA加速? (y/n, 默认y): " use_cuda
use_cuda=${use_cuda:-y}

# 询问并发数
read -p "请输入最大并发数 (默认5, 适合16G显存): " max_workers
max_workers=${max_workers:-5}

# 询问是否使用TensorBoard
read -p "是否使用TensorBoard记录训练过程? (y/n, 默认n): " use_tensorboard
use_tensorboard=${use_tensorboard:-n}

# 如果使用TensorBoard，询问是否记录权重
log_weights="n"
if [[ "$use_tensorboard" =~ ^[Yy]$ ]]; then
    read -p "是否记录网络权重到TensorBoard? (y/n, 默认n): " log_weights
    log_weights=${log_weights:-n}
fi

# 构建命令
cmd="python parallel_train.py -env $env_name"

# 根据预设选择参数
if [ "$preset_name" = "gpu_optimized" ]; then
    cmd="$cmd -seeds 1 2 3 4 5 -workers $max_workers"
else
    cmd="$cmd -preset $preset_name -workers $max_workers"
fi

if [[ "$use_cuda" =~ ^[Yy]$ ]]; then
    echo "✅ 启用CUDA加速"
fi

# 添加TensorBoard参数
if [[ "$use_tensorboard" =~ ^[Yy]$ ]]; then
    cmd="$cmd -use_tensorboard"
    echo "✅ 启用TensorBoard记录"
    
    if [[ "$log_weights" =~ ^[Yy]$ ]]; then
        cmd="$cmd -log_weights"
        echo "✅ 启用权重记录"
    fi
fi

echo
echo "🚀 即将执行的命令:"
echo "$cmd"
echo
read -p "确认开始训练? (y/n): " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 0
fi

echo
echo "🎯 开始并行训练..."
echo "========================================"

# 执行训练
echo "y" | $cmd

echo
echo "========================================"
echo "🏁 训练完成!"
echo "📁 结果保存在: parallel_experiments 目录"
if [[ "$use_tensorboard" =~ ^[Yy]$ ]]; then
    echo "📊 TensorBoard日志保存在各实验目录的 tensorboard 文件夹中"
    echo "📈 查看训练过程: tensorboard --logdir parallel_experiments"
    echo "🌐 然后在浏览器中打开: http://localhost:6006"
fi
echo