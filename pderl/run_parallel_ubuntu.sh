#!/bin/bash

# PDERL 并行训练脚本 - Ubuntu版本
# 修复training.log为空的问题

# 设置UTF-8编码
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# 确保脚本在出错时退出
set -e

echo "========================================"
echo "PDERL 并行训练脚本 (Ubuntu修复版)"
echo "直接启动5个并行实例 + 消融实验支持"
echo "========================================"
echo

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 找不到python命令"
    echo "💡 请确保Python已正确安装并在PATH中"
    exit 1
fi

echo "✅ Python版本: $(python --version)"
echo "✅ 当前环境: ${CONDA_DEFAULT_ENV:-系统Python}"
echo

# 检查run_pderl.py是否存在
if [ ! -f "run_pderl.py" ]; then
    echo "❌ 错误: 找不到run_pderl.py文件"
    echo "💡 请确保在正确的目录中运行此脚本"
    exit 1
fi

echo "✅ 找到run_pderl.py文件"
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

# 询问是否使用TensorBoard
read -p "是否使用TensorBoard记录训练过程? (y/n, 默认n): " use_tensorboard
use_tensorboard=${use_tensorboard:-n}

# 新增：消融实验选择
echo
echo "🧪 请选择实验类型:"
echo "  1. 标准PDERL训练 (默认配置)"
echo "  2. 消融实验 - 禁用近端变异 (Proximal Mutation)"
echo "  3. 消融实验 - 禁用蒸馏交叉 (Distillation Crossover)"
echo "  4. 消融实验 - 禁用新颖性搜索 (Novelty Search)"
echo "  5. 消融实验 - 禁用近端变异+蒸馏交叉"
echo "  6. 消融实验 - 禁用所有高级特性 (仅基础DDPG+EA)"
echo "  7. 自定义参数配置"
echo
read -p "请输入实验类型编号 (1-7, 默认1): " exp_choice
exp_choice=${exp_choice:-1}

# 根据选择设置消融实验参数
ablation_params=""
exp_suffix=""

case $exp_choice in
    1) 
        echo "✅ 选择: 标准PDERL训练"
        ablation_params="-proximal_mut -distil"
        exp_suffix="_standard"
        ;;
    2) 
        echo "✅ 选择: 消融实验 - 禁用近端变异"
        ablation_params="-distil"
        exp_suffix="_no_proximal_mut"
        ;;
    3) 
        echo "✅ 选择: 消融实验 - 禁用蒸馏交叉"
        ablation_params="-proximal_mut"
        exp_suffix="_no_distil"
        ;;
    4) 
        echo "✅ 选择: 消融实验 - 禁用新颖性搜索"
        ablation_params="-proximal_mut -distil"
        exp_suffix="_no_novelty"
        ;;
    5) 
        echo "✅ 选择: 消融实验 - 禁用近端变异+蒸馏交叉"
        ablation_params=""
        exp_suffix="_no_proximal_distil"
        ;;
    6) 
        echo "✅ 选择: 消融实验 - 禁用所有高级特性"
        ablation_params=""
        exp_suffix="_baseline"
        ;;
    7) 
        echo "✅ 选择: 自定义参数配置"
        echo
        echo "🔧 可用的高级特性参数:"
        echo "  - 近端变异 (Proximal Mutation): 提高变异安全性"
        echo "  - 蒸馏交叉 (Distillation Crossover): 智能交叉策略"
        echo "  - 新颖性搜索 (Novelty Search): 探索多样性"
        echo
        read -p "是否启用近端变异? (y/n, 默认y): " enable_proximal
        read -p "是否启用蒸馏交叉? (y/n, 默认y): " enable_distil
        read -p "是否启用新颖性搜索? (y/n, 默认n): " enable_novelty
        read -p "变异幅度 (0.01-0.2, 默认0.05): " mut_mag
        
        enable_proximal=${enable_proximal:-y}
        enable_distil=${enable_distil:-y}
        enable_novelty=${enable_novelty:-n}
        mut_mag=${mut_mag:-0.05}
        
        ablation_params=""
        exp_suffix="_custom"
        
        if [[ "$enable_proximal" =~ ^[Yy]$ ]]; then
            ablation_params="$ablation_params -proximal_mut"
            exp_suffix="${exp_suffix}_prox"
        fi
        
        if [[ "$enable_distil" =~ ^[Yy]$ ]]; then
            ablation_params="$ablation_params -distil"
            exp_suffix="${exp_suffix}_dist"
        fi
        
        if [[ "$enable_novelty" =~ ^[Yy]$ ]]; then
            ablation_params="$ablation_params -novelty"
            exp_suffix="${exp_suffix}_nov"
        fi
        
        ablation_params="$ablation_params -mut_mag $mut_mag"
        exp_suffix="${exp_suffix}_mag${mut_mag}"
        ;;
    *) 
        echo "❌ 无效的实验类型选择，使用默认配置"
        ablation_params="-proximal_mut -distil"
        exp_suffix="_standard"
        ;;
esac

# 创建实验目录
exp_dir="parallel_experiments/${env_name}${exp_suffix}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$exp_dir"

echo "📁 实验目录: $exp_dir"
echo
echo "🚀 即将启动5个并行训练实例..."
echo "每个实例使用不同的随机种子 (1, 3, 7, 10, 100)"
echo
read -p "确认开始训练? (y/n): " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 0
fi

echo
echo "🎯 开始并行训练..."
echo "========================================"

# 存储进程ID
pids=()

# 启动5个并行实例
for seed in 1 3 7 10 100; do
    instance_dir="${exp_dir}/seed_${seed}"
    mkdir -p "$instance_dir"
    
    # 构建命令
    cmd="python run_pderl.py -env $env_name -seed $seed -logdir $instance_dir"
    
    # 添加消融实验参数
    if [ -n "$ablation_params" ]; then
        cmd="$cmd $ablation_params"
    fi
    
    # 添加TensorBoard参数
    if [[ "$use_tensorboard" =~ ^[Yy]$ ]]; then
        cmd="$cmd -use_tensorboard"
    fi
    
    echo "🚀 启动实例 $seed: $cmd"
    
    # 创建启动脚本来确保输出重定向正常工作
    start_script="${instance_dir}/start_training.sh"
    cat > "$start_script" << EOF
#!/bin/bash
cd "$(pwd)"
export PYTHONUNBUFFERED=1
exec $cmd
EOF
    chmod +x "$start_script"
    
    # 在后台运行并重定向输出
    # 使用exec确保输出立即写入文件
    nohup bash "$start_script" > "${instance_dir}/training.log" 2>&1 &
    
    # 记录进程ID
    pids+=($!)
    
    echo "✅ 实例 $seed 已启动 (PID: $!)" 
    echo "📝 日志文件: ${instance_dir}/training.log"
    
    # 短暂延迟避免同时启动造成资源冲突
    sleep 3
    
    # 检查进程是否成功启动
    sleep 2
    if ! kill -0 $! 2>/dev/null; then
        echo "⚠️ 警告: 实例 $seed 可能启动失败"
        echo "📋 检查日志: cat ${instance_dir}/training.log"
    else
        echo "✅ 实例 $seed 运行正常"
    fi
    echo
done

echo
echo "📊 所有实例已启动，进程ID: ${pids[@]}"
echo "📁 日志文件保存在各自的目录中"
echo

# 等待一段时间让训练开始
echo "⏳ 等待10秒让训练初始化..."
sleep 10

echo
echo "📈 监控训练进度:"
echo "  - 查看日志: tail -f ${exp_dir}/seed_1/training.log"
echo "  - 实时监控: watch 'tail -n 5 ${exp_dir}/seed_*/training.log'"
echo "  - 检查进程: ps aux | grep run_pderl"
echo "  - 检查日志大小: ls -lh ${exp_dir}/seed_*/training.log"
if [[ "$use_tensorboard" =~ ^[Yy]$ ]]; then
    echo "  - TensorBoard: tensorboard --logdir $exp_dir"
fi
echo
echo "⏹️ 停止所有训练: kill ${pids[@]}"
echo "🧹 清理进程: pkill -f 'run_pderl.py'"
echo

# 显示初始日志内容
echo "📋 检查初始日志内容:"
for seed in 1 3 7 10 100; do
    log_file="${exp_dir}/seed_${seed}/training.log"
    if [ -f "$log_file" ]; then
        log_size=$(stat -c%s "$log_file" 2>/dev/null || echo "0")
        echo "  - seed_${seed}: ${log_size} bytes"
        if [ "$log_size" -gt 0 ]; then
            echo "    前几行内容:"
            head -n 3 "$log_file" | sed 's/^/      /'
        else
            echo "    ⚠️ 日志文件为空"
        fi
    else
        echo "  - seed_${seed}: 日志文件不存在"
    fi
done

echo
echo "🏁 训练将在后台继续运行..."
echo "💡 提示: 如果日志文件为空，可能需要检查Python环境或依赖包"
echo "🔧 调试命令: python run_pderl.py -env $env_name -seed 1 -logdir test_debug"
echo "📊 实验配置: $ablation_params"
echo "📁 实验类型: $exp_suffix"
echo "========================================"