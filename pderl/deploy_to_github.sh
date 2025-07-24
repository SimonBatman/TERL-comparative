#!/bin/bash

# PDERL项目GitHub部署脚本
# 用于将代码上传到GitHub并准备云平台部署

echo "========================================"
echo "PDERL GitHub部署脚本"
echo "========================================"
echo

# 检查git是否已初始化
if [ ! -d ".git" ]; then
    echo "🔧 初始化Git仓库..."
    git init
    echo "✅ Git仓库已初始化"
else
    echo "✅ Git仓库已存在"
fi

# 创建.gitignore文件
echo "📝 创建.gitignore文件..."
cat > .gitignore << 'EOF'
# Python缓存文件
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
PIPFILE.lock

# 虚拟环境
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE文件
.vscode/
.idea/
*.swp
*.swo
*~

# 实验结果和日志
parallel_experiments/
test_*/
demo_test/
*.log
*.pkl
*.pt
*.pth

# 系统文件
.DS_Store
Thumbs.db

# MuJoCo
.mujoco/
mjkey.txt

# 临时文件
*.tmp
*.temp
*.bak

# 大文件
*.mp4
*.avi
*.gif
*.png
*.jpg
*.jpeg
EOF

echo "✅ .gitignore文件已创建"

# 添加所有文件
echo "📦 添加文件到Git..."
git add .

# 检查是否有文件被添加
if git diff --cached --quiet; then
    echo "⚠️ 没有新文件需要提交"
else
    echo "✅ 文件已添加到暂存区"
fi

# 提交更改
echo "💾 提交更改..."
read -p "请输入提交信息 (默认: 'Initial commit for cloud deployment'): " commit_msg
commit_msg=${commit_msg:-"Initial commit for cloud deployment"}

git commit -m "$commit_msg"

if [ $? -eq 0 ]; then
    echo "✅ 提交成功"
else
    echo "⚠️ 没有新的更改需要提交"
fi

# 询问GitHub仓库信息
echo
echo "🔗 GitHub仓库配置"
read -p "请输入GitHub用户名: " github_username
read -p "请输入仓库名称 (默认: TERL-comparative): " repo_name
repo_name=${repo_name:-"TERL-comparative"}

# 设置远程仓库
remote_url="https://github.com/$github_username/$repo_name.git"
echo "🌐 设置远程仓库: $remote_url"

# 检查是否已有远程仓库
if git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️ 远程仓库已存在，更新URL..."
    git remote set-url origin "$remote_url"
else
    git remote add origin "$remote_url"
fi

echo "✅ 远程仓库已配置"

# 推送到GitHub
echo
echo "🚀 推送到GitHub..."
echo "注意：首次推送可能需要输入GitHub用户名和密码/token"
echo

read -p "确认推送到GitHub? (y/n): " confirm_push
if [[ "$confirm_push" =~ ^[Yy]$ ]]; then
    # 设置默认分支为main
    git branch -M main
    
    # 推送到远程仓库
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo "✅ 代码已成功推送到GitHub!"
        echo "📍 仓库地址: $remote_url"
    else
        echo "❌ 推送失败，请检查网络连接和GitHub凭据"
        echo "💡 提示："
        echo "   1. 确保GitHub仓库已创建"
        echo "   2. 检查用户名和密码/token是否正确"
        echo "   3. 如果使用token，确保有足够的权限"
    fi
else
    echo "❌ 已取消推送"
fi

echo
echo "========================================"
echo "📋 云平台部署说明"
echo "========================================"
echo
echo "在云平台上执行以下命令来部署项目:"
echo
echo "1. 克隆仓库:"
echo "   git clone $remote_url"
echo "   cd $repo_name/pderl"
echo
echo "2. 设置环境:"
echo "   conda create -n erl_env python=3.8"
echo "   conda activate erl_env"
echo "   conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia"
echo "   pip install -r requirements.txt"
echo
echo "3. 运行训练:"
echo "   chmod +x run_parallel_experiments.sh"
echo "   ./run_parallel_experiments.sh"
echo
echo "详细部署指南请参考: CLOUD_DEPLOYMENT.md"
echo
echo "🎉 部署脚本执行完成!"
echo