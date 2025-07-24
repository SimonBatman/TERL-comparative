#!/bin/bash

# PDERL云平台快速部署脚本
# 在Linux云平台上一键设置环境和开始训练

set -e  # 遇到错误立即退出

echo "========================================"
echo "PDERL 云平台快速部署脚本"
echo "========================================"
echo

# 检查系统信息
echo "🖥️ 系统信息:"
echo "操作系统: $(uname -s)"
echo "内核版本: $(uname -r)"
echo "架构: $(uname -m)"
echo

# 检查NVIDIA GPU
echo "🎮 检查GPU信息..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
    echo "✅ NVIDIA GPU检测成功"
else
    echo "⚠️ 未检测到NVIDIA GPU或nvidia-smi命令"
fi
echo

# 检查conda
echo "🐍 检查Conda环境..."
if command -v conda &> /dev/null; then
    echo "✅ Conda已安装: $(conda --version)"
else
    echo "❌ Conda未安装，请先安装Miniconda或Anaconda"
    echo "下载地址: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi
echo

# 创建conda环境
echo "🔧 创建conda环境..."
if conda env list | grep -q "erl_env"; then
    echo "⚠️ erl_env环境已存在"
    read -p "是否删除并重新创建? (y/n): " recreate
    if [[ "$recreate" =~ ^[Yy]$ ]]; then
        conda env remove -n erl_env -y
        echo "🗑️ 已删除旧环境"
    else
        echo "📦 使用现有环境"
    fi
fi

if ! conda env list | grep -q "erl_env"; then
    echo "📦 创建新的erl_env环境..."
    conda create -n erl_env python=3.8 -y
    echo "✅ 环境创建成功"
fi

# 激活环境
echo "🔄 激活环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate erl_env
echo "✅ 环境已激活: $CONDA_DEFAULT_ENV"
echo

# 安装PyTorch (CUDA版本)
echo "🔥 安装PyTorch (CUDA版本)..."
echo "这可能需要几分钟时间..."
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y
echo "✅ PyTorch安装完成"
echo

# 验证CUDA
echo "🧪 验证CUDA支持..."
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
python -c "import torch; print('GPU count:', torch.cuda.device_count())"
if python -c "import torch; print(torch.cuda.is_available())" | grep -q "True"; then
    python -c "import torch; print('GPU name:', torch.cuda.get_device_name(0))"
    echo "✅ CUDA支持验证成功"
else
    echo "⚠️ CUDA支持验证失败，将使用CPU训练"
fi
echo

# 安装其他依赖
echo "📦 安装项目依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ 依赖安装完成"
else
    echo "⚠️ requirements.txt文件不存在，手动安装核心依赖..."
    pip install numpy scipy matplotlib seaborn pandas gym mujoco-py psutil tqdm
fi
echo

# 设置MuJoCo (如果需要)
echo "🤖 检查MuJoCo环境..."
if python -c "import mujoco_py" 2>/dev/null; then
    echo "✅ MuJoCo环境正常"
else
    echo "⚠️ MuJoCo环境可能需要额外配置"
    echo "如果遇到问题，请参考: https://github.com/openai/mujoco-py"
fi
echo

# 测试环境
echo "🧪 测试训练环境..."
if python -c "import gym; env = gym.make('Walker2d-v2'); print('✅ Walker2d-v2环境测试成功')" 2>/dev/null; then
    echo "✅ 训练环境测试通过"
else
    echo "⚠️ 训练环境测试失败，可能需要额外配置"
fi
echo

# 显示可用的训练选项
echo "========================================"
echo "🚀 环境设置完成！可用的训练选项:"
echo "========================================"
echo
echo "1. 交互式训练 (推荐):"
echo "   ./run_parallel_experiments.sh"
echo
echo "2. GPU优化训练 (16G显存):"
echo "   python parallel_train.py -env Walker2d-v2 -preset gpu_optimized -workers 5"
echo
echo "3. 快速测试:"
echo "   python parallel_train.py -env Hopper-v2 -preset quick_test -workers 3"
echo
echo "4. 自定义训练:"
echo "   python parallel_train.py -env HalfCheetah-v2 -seeds 1 2 3 4 5 -workers 5"
echo
echo "5. 查看所有预设:"
echo "   python parallel_train.py --list-presets"
echo
echo "📊 系统资源监控:"
echo "   watch -n 1 nvidia-smi  # GPU监控"
echo "   htop                   # CPU/内存监控"
echo
echo "📁 训练结果将保存在: parallel_experiments/"
echo "📖 详细文档: CLOUD_DEPLOYMENT.md"
echo
echo "🎉 部署完成！现在可以开始训练了。"
echo

# 询问是否立即开始训练
read -p "是否立即开始GPU优化训练? (y/n): " start_training
if [[ "$start_training" =~ ^[Yy]$ ]]; then
    echo "🚀 启动GPU优化训练..."
    echo "y" | python parallel_train.py -env Walker2d-v2 -preset gpu_optimized -workers 5
else
    echo "💡 稍后可以手动运行训练命令"
fi

echo "✨ 脚本执行完成！"