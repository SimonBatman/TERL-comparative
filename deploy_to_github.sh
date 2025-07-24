#!/bin/bash

# TERL-Comparative GitHub部署脚本

echo "🚀 开始部署TERL-Comparative项目到GitHub..."

# 检查是否已经配置了git用户信息
if [ -z "$(git config user.name)" ] || [ -z "$(git config user.email)" ]; then
    echo "⚠️  请先配置Git用户信息:"
    echo "git config --global user.name \"Your Name\""
    echo "git config --global user.email \"your.email@example.com\""
    exit 1
fi

# 检查是否有远程仓库
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "📝 请添加GitHub远程仓库:"
    echo "git remote add origin https://github.com/yourusername/TERL-comparative.git"
    echo "或者:"
    echo "git remote add origin git@github.com:yourusername/TERL-comparative.git"
    exit 1
fi

# 推送到GitHub
echo "📤 推送到GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ 成功推送到GitHub!"
    echo "🌐 访问您的仓库: $(git remote get-url origin)"
else
    echo "❌ 推送失败，请检查网络连接和权限"
    exit 1
fi

echo "📋 项目结构说明:"
echo "├── ERL/          # ERL算法实现"
echo "├── pderl/        # PDERL算法实现 (带TensorBoard支持)"
echo "├── results/      # 实验结果"
echo "└── README.md     # 项目说明"

echo ""
echo "💡 建议的下一步:"
echo "1. 在GitHub上创建Release标签"
echo "2. 添加详细的实验结果和分析"
echo "3. 完善文档和使用说明"
echo "4. 考虑添加CI/CD流水线"
