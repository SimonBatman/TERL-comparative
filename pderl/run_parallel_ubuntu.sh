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
echo "直接启动5个并行实例"
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

# 创建实验目录
exp_dir="parallel_experiments/${env_name}_$(date +%Y%m%d_%H%M%S)"
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
echo "========================================"