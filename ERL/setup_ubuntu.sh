#!/bin/bash
# ERL项目Ubuntu自动化安装脚本
# 适用于腾讯云Cloud Studio等Ubuntu云平台

set -e  # 遇到错误立即退出

echo "🚀 开始ERL项目Ubuntu环境配置..."
echo "================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warn "检测到root用户，某些操作可能需要调整"
    fi
}

# 更新系统包
update_system() {
    log_info "更新系统包..."
    sudo apt update -y
    sudo apt upgrade -y
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖包..."
    sudo apt install -y \
        build-essential \
        cmake \
        git \
        curl \
        ca-certificates \
        libjpeg-dev \
        libpng-dev \
        libgl1-mesa-dev \
        libgl1-mesa-glx \
        libglew-dev \
        libosmesa6-dev \
        software-properties-common \
        net-tools \
        vim \
        wget \
        xvfb \
        xserver-xorg-dev \
        libglfw3-dev \
        patchelf \
        htop
}

# 检查conda是否存在
check_conda() {
    if command -v conda &> /dev/null; then
        log_info "检测到conda，版本: $(conda --version)"
        return 0
    else
        log_warn "未检测到conda，将使用pip安装"
        return 1
    fi
}

# 安装MuJoCo
install_mujoco() {
    log_info "安装MuJoCo..."
    
    # 创建MuJoCo目录
    mkdir -p ~/.mujoco
    
    # 检查是否已安装
    if [ -d "~/.mujoco/mujoco210" ]; then
        log_info "MuJoCo已存在，跳过下载"
    else
        # 下载MuJoCo
        cd /tmp
        wget -q https://mujoco.org/download/mujoco210-linux-x86_64.tar.gz
        tar -xf mujoco210-linux-x86_64.tar.gz
        mv mujoco210 ~/.mujoco/
        rm mujoco210-linux-x86_64.tar.gz
    fi
    
    # 设置环境变量
    if ! grep -q "MUJOCO" ~/.bashrc; then
        echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/.mujoco/mujoco210/bin' >> ~/.bashrc
        echo 'export MUJOCO_PY_MUJOCO_PATH=~/.mujoco/mujoco210' >> ~/.bashrc
        echo 'export MUJOCO_GL=osmesa' >> ~/.bashrc
    fi
}

# 设置虚拟显示
setup_display() {
    log_info "配置虚拟显示..."
    
    if ! grep -q "DISPLAY=:99" ~/.bashrc; then
        echo 'export DISPLAY=:99' >> ~/.bashrc
    fi
    
    # 启动虚拟显示
    if ! pgrep -f "Xvfb :99" > /dev/null; then
        Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
        log_info "虚拟显示已启动"
    fi
}

# 使用conda安装环境
install_with_conda() {
    log_info "使用conda创建环境..."
    
    # 检查环境是否已存在
    if conda env list | grep -q "ERL_Ubuntu"; then
        log_warn "环境ERL_Ubuntu已存在，是否删除重建？(y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            conda env remove -n ERL_Ubuntu -y
        else
            log_info "使用现有环境"
            return 0
        fi
    fi
    
    # 获取脚本所在目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # 创建环境
    if [ -f "$SCRIPT_DIR/environment_ubuntu.yml" ]; then
        conda env create -f "$SCRIPT_DIR/environment_ubuntu.yml"
    elif [ -f "./environment_ubuntu.yml" ]; then
        conda env create -f "./environment_ubuntu.yml"
    elif [ -f "environment_ubuntu.yml" ]; then
        conda env create -f "environment_ubuntu.yml"
    else
        log_error "未找到environment_ubuntu.yml文件，已检查路径："
        log_error "  - $SCRIPT_DIR/environment_ubuntu.yml"
        log_error "  - ./environment_ubuntu.yml"
        log_error "  - environment_ubuntu.yml"
        return 1
    fi
}

# 使用pip安装
install_with_pip() {
    log_info "使用pip安装依赖..."
    
    # 升级pip
    pip install --upgrade pip
    
    # 获取脚本所在目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # 安装依赖
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        pip install -r "$SCRIPT_DIR/requirements.txt"
    elif [ -f "./requirements.txt" ]; then
        pip install -r "./requirements.txt"
    elif [ -f "requirements.txt" ]; then
        pip install -r "requirements.txt"
    else
        log_error "未找到requirements.txt文件，已检查路径："
        log_error "  - $SCRIPT_DIR/requirements.txt"
        log_error "  - ./requirements.txt"
        log_error "  - requirements.txt"
        return 1
    fi
}

# 测试安装
test_installation() {
    log_info "测试安装结果..."
    
    # 测试基础包导入
    python -c "import numpy, matplotlib, scipy; print('✅ 基础科学计算包正常')" || log_error "基础包导入失败"
    
    # 测试机器学习框架
    python -c "import tensorflow, torch; print('✅ 机器学习框架正常')" || log_warn "机器学习框架可能有问题"
    
    # 测试Gym
    python -c "import gym; print('✅ Gym环境正常')" || log_error "Gym导入失败"
    
    # 测试MuJoCo
    python -c "import mujoco_py; print('✅ MuJoCo正常')" || log_warn "MuJoCo可能需要额外配置"
    
    # 测试环境创建
    python -c "import gym; env = gym.make('Reacher-v2'); print('✅ Reacher-v2环境创建成功')" || log_warn "环境创建可能有问题"
}

# 创建启动脚本
create_run_script() {
    log_info "创建运行脚本..."
    
    cat > run_erl_ubuntu.sh << 'EOF'
#!/bin/bash
# ERL训练启动脚本

# 设置环境变量
export DISPLAY=:99
export MUJOCO_GL=osmesa
source ~/.bashrc

# 启动虚拟显示（如果未运行）
if ! pgrep -f "Xvfb :99" > /dev/null; then
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    echo "虚拟显示已启动"
fi

# 激活conda环境（如果使用conda）
if command -v conda &> /dev/null && conda env list | grep -q "ERL_Ubuntu"; then
    conda activate ERL_Ubuntu
fi

# 运行训练
echo "开始ERL训练..."
python run_erl.py "$@"
EOF

    chmod +x run_erl_ubuntu.sh
    log_info "运行脚本已创建: ./run_erl_ubuntu.sh"
}

# 显示使用说明
show_usage() {
    echo ""
    echo "🎉 ERL环境配置完成！"
    echo "================================================"
    echo "使用方法:"
    echo ""
    echo "1. 重新加载环境变量:"
    echo "   source ~/.bashrc"
    echo ""
    echo "2. 激活conda环境 (如果使用conda):"
    echo "   conda activate ERL_Ubuntu"
    echo ""
    echo "3. 运行训练:"
    echo "   ./run_erl_ubuntu.sh --env Reacher-v2 --seed 0"
    echo "   或者直接: python run_erl.py --env Reacher-v2 --seed 0"
    echo ""
    echo "4. 生成结果图表:"
    echo "   python plotting_results/plot_erl_final.py --env all"
    echo ""
    echo "5. 并行训练多个环境:"
    echo "   ./run_parallel.sh"
    echo ""
    echo "📚 详细文档请参考: UBUNTU_DEPLOYMENT.md"
    echo "================================================"
}

# 主函数
main() {
    log_info "开始ERL项目Ubuntu环境配置"
    
    check_root
    update_system
    install_system_deps
    install_mujoco
    setup_display
    
    # 尝试conda安装，失败则使用pip
    if check_conda; then
        if install_with_conda; then
            log_info "Conda环境安装成功"
        else
            log_warn "Conda安装失败，尝试pip安装"
            install_with_pip
        fi
    else
        install_with_pip
    fi
    
    # 重新加载环境变量
    source ~/.bashrc
    
    test_installation
    create_run_script
    show_usage
    
    log_info "安装完成！请运行 'source ~/.bashrc' 重新加载环境变量"
}

# 错误处理
trap 'log_error "安装过程中出现错误，请检查日志"' ERR

# 运行主函数
main "$@"