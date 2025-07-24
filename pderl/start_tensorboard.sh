#!/bin/bash

# TensorBoard快速启动脚本
# 用于在云平台上快速启动TensorBoard服务

echo "======================================"
echo "TensorBoard 快速启动脚本"
echo "======================================"
echo

# 检查TensorBoard是否已安装
if ! command -v tensorboard &> /dev/null; then
    echo "❌ TensorBoard未安装"
    echo "💡 请运行: pip install tensorboard"
    exit 1
fi

echo "✅ TensorBoard已安装"
echo

# 设置默认参数
DEFAULT_LOGDIR="parallel_experiments"
DEFAULT_PORT="6006"
DEFAULT_HOST="0.0.0.0"

# 询问日志目录
read -p "请输入日志目录 (默认: $DEFAULT_LOGDIR): " logdir
logdir=${logdir:-$DEFAULT_LOGDIR}

# 检查日志目录是否存在
if [ ! -d "$logdir" ]; then
    echo "⚠️ 警告: 目录 '$logdir' 不存在"
    read -p "是否创建该目录? (y/n): " create_dir
    if [[ "$create_dir" =~ ^[Yy]$ ]]; then
        mkdir -p "$logdir"
        echo "✅ 已创建目录: $logdir"
    else
        echo "❌ 已取消"
        exit 1
    fi
fi

# 询问端口
read -p "请输入端口号 (默认: $DEFAULT_PORT): " port
port=${port:-$DEFAULT_PORT}

# 询问主机地址
read -p "请输入主机地址 (默认: $DEFAULT_HOST): " host
host=${host:-$DEFAULT_HOST}

# 询问是否后台运行
read -p "是否在后台运行? (y/n, 默认n): " background
background=${background:-n}

echo
echo "📊 TensorBoard配置:"
echo "   日志目录: $logdir"
echo "   端口: $port"
echo "   主机: $host"
echo "   后台运行: $background"
echo

# 构建命令
cmd="tensorboard --logdir=$logdir --port=$port --host=$host"

if [[ "$background" =~ ^[Yy]$ ]]; then
    # 后台运行
    echo "🚀 在后台启动TensorBoard..."
    nohup $cmd > tensorboard.log 2>&1 &
    tb_pid=$!
    echo "✅ TensorBoard已在后台启动 (PID: $tb_pid)"
    echo "📄 日志文件: tensorboard.log"
    echo "🛑 停止服务: kill $tb_pid"
else
    # 前台运行
    echo "🚀 启动TensorBoard..."
    echo "🛑 按 Ctrl+C 停止服务"
    echo
fi

echo "🌐 访问地址:"
if [ "$host" = "0.0.0.0" ]; then
    echo "   本地: http://localhost:$port"
    echo "   远程: http://your-server-ip:$port"
else
    echo "   访问: http://$host:$port"
fi
echo

if [[ "$background" =~ ^[Yy]$ ]]; then
    echo "💡 提示:"
    echo "   - 查看日志: tail -f tensorboard.log"
    echo "   - 检查进程: ps aux | grep tensorboard"
    echo "   - 停止服务: kill $tb_pid 或 pkill -f tensorboard"
else
    echo "💡 提示: 确保云平台已开放端口 $port"
    echo
    # 前台运行TensorBoard
    exec $cmd
fi