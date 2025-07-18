# ERL项目Ubuntu云平台部署指南

本指南专门针对从Windows系统迁移到Ubuntu云平台（如腾讯云Cloud Studio）的部署流程。

## 🚀 快速部署流程

### 1. 环境准备

#### 方案A：使用Conda环境（推荐）
```bash
# 下载项目代码
git clone https://github.com/SimonBatman/TERL-comparative.git
cd TERL-comparative

# 创建conda环境
conda env create -f environment_ubuntu.yml
conda activate ERL_Ubuntu
```

#### 方案B：使用pip安装（备选）
```bash
# 如果conda方案失败，使用pip
pip install -r requirements.txt
```

### 2. 系统依赖安装

```bash
# 更新系统包
sudo apt update
sudo apt upgrade -y

# 安装系统依赖
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
    virtualenv \
    wget \
    xpra \
    xserver-xorg-dev \
    libglfw3-dev \
    patchelf

# 安装MuJoCo依赖
sudo apt install -y libosmesa6-dev libgl1-mesa-glx libglfw3
```

### 3. MuJoCo配置

```bash
# 下载MuJoCo
wget https://mujoco.org/download/mujoco210-linux-x86_64.tar.gz
tar -xf mujoco210-linux-x86_64.tar.gz

# 创建MuJoCo目录
mkdir -p ~/.mujoco
mv mujoco210 ~/.mujoco/

# 设置环境变量
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/.mujoco/mujoco210/bin' >> ~/.bashrc
echo 'export MUJOCO_PY_MUJOCO_PATH=~/.mujoco/mujoco210' >> ~/.bashrc
source ~/.bashrc
```

### 4. 显示设置（无头模式）

```bash
# 安装虚拟显示
sudo apt install -y xvfb

# 设置虚拟显示环境变量
echo 'export DISPLAY=:99' >> ~/.bashrc
source ~/.bashrc

# 启动虚拟显示（在运行训练前执行）
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
```

## 🔧 常见问题解决

### 问题1：MuJoCo安装失败

**错误信息**：`ERROR: Could not find a version that satisfies the requirement mujoco-py`

**解决方案**：
```bash
# 先安装系统依赖
sudo apt install -y libosmesa6-dev libgl1-mesa-glx libglfw3

# 设置编译环境
export CC=/usr/bin/gcc
export CXX=/usr/bin/g++

# 重新安装
pip install mujoco-py==2.1.2.14
```

### 问题2：TensorFlow版本冲突

**错误信息**：`tensorflow` 版本不兼容

**解决方案**：
```bash
# 卸载现有tensorflow
pip uninstall tensorflow tensorflow-gpu

# 安装CPU版本
pip install tensorflow==1.15.0
```

### 问题3：PyTorch CUDA版本问题

**解决方案**：
```bash
# 检查CUDA版本
nvcc --version

# 根据CUDA版本安装对应PyTorch
# CUDA 11.1
pip install torch==1.8.1+cu111 torchvision==0.9.1+cu111 -f https://download.pytorch.org/whl/torch_stable.html

# CPU版本（如果没有GPU）
pip install torch==1.8.1+cpu torchvision==0.9.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
```

### 问题4：Gym环境渲染问题

**错误信息**：`DISPLAY` 相关错误

**解决方案**：
```bash
# 启动虚拟显示
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99

# 或者使用无头模式
export MUJOCO_GL=osmesa
```

## 🎯 运行验证

### 1. 测试环境

```bash
# 测试Python导入
python -c "import gym, tensorflow, torch, numpy, matplotlib; print('All packages imported successfully!')"

# 测试MuJoCo
python -c "import mujoco_py; print('MuJoCo-py imported successfully!')"

# 测试Gym环境
python -c "import gym; env = gym.make('Reacher-v2'); print('Gym environment created successfully!')"
```

### 2. 运行训练

```bash
# 设置虚拟显示
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99

# 运行单个实验
python run_erl.py --env Reacher-v2 --seed 0

# 运行多个种子（利用云平台算力）
for seed in 0 1 2 3 4; do
    python run_erl.py --env Reacher-v2 --seed $seed &
done
wait
```

## 📊 性能优化建议

### 1. 并行训练

```bash
# 创建并行训练脚本
cat > run_parallel.sh << 'EOF'
#!/bin/bash

# 设置环境
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# 并行运行多个环境
envs=("Reacher-v2" "Ant-v2" "HalfCheetah-v2" "Swimmer-v2")
seeds=(0 1 2)

for env in "${envs[@]}"; do
    for seed in "${seeds[@]}"; do
        echo "Starting $env with seed $seed"
        python run_erl.py --env $env --seed $seed > logs/${env}_${seed}.log 2>&1 &
        
        # 控制并发数量，避免资源耗尽
        if (( $(jobs -r | wc -l) >= 4 )); then
            wait -n  # 等待任意一个任务完成
        fi
    done
done

wait  # 等待所有任务完成
echo "All experiments completed!"
EOF

chmod +x run_parallel.sh
```

### 2. 资源监控

```bash
# 监控GPU使用
watch -n 1 nvidia-smi

# 监控CPU和内存
htop

# 监控磁盘空间
df -h
```

## 🔄 结果同步

### 1. 实时监控

```bash
# 使用TensorBoard监控训练
tensorboard --logdir=runs --host=0.0.0.0 --port=6006
```

### 2. 结果下载

```bash
# 生成结果图表
python plotting_results/plot_erl_final.py --env all

# 打包结果
tar -czf erl_results.tar.gz plotting_results/*.png runs/

# 上传到云存储或通过其他方式下载
```

## 📝 注意事项

1. **内存管理**：云平台内存有限，避免同时运行过多实验
2. **存储空间**：定期清理不必要的日志文件
3. **网络稳定性**：长时间训练建议使用screen或tmux
4. **备份策略**：重要结果及时备份到云存储

## 🆘 故障排除

如果遇到其他问题，可以：

1. 检查系统日志：`dmesg | tail`
2. 检查Python环境：`conda list` 或 `pip list`
3. 验证GPU可用性：`nvidia-smi`
4. 测试网络连接：`ping google.com`

---

**部署成功后，您就可以充分利用云平台的算力优势进行大规模ERL实验了！**