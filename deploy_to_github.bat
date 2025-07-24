@echo off
chcp 65001 >nul
echo 🚀 开始部署TERL-Comparative项目到GitHub...

REM 检查Git配置
git config user.name >nul 2>&1
if errorlevel 1 (
    echo ⚠️  请先配置Git用户信息:
    echo git config --global user.name "Your Name"
    echo git config --global user.email "your.email@example.com"
    pause
    exit /b 1
)

REM 检查远程仓库
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo 📝 请添加GitHub远程仓库:
    echo git remote add origin https://github.com/yourusername/TERL-comparative.git
    echo 或者:
    echo git remote add origin git@github.com:yourusername/TERL-comparative.git
    pause
    exit /b 1
)

REM 推送到GitHub
echo 📤 推送到GitHub...
git push -u origin main

if errorlevel 1 (
    echo ❌ 推送失败，请检查网络连接和权限
    pause
    exit /b 1
)

echo ✅ 成功推送到GitHub!
echo.
echo 📋 当前项目结构:
echo ├── ERL/          # ERL算法实现
echo ├── pderl/        # PDERL算法实现 (带TensorBoard支持)
echo ├── results/      # 实验结果
echo └── README.md     # 项目说明
echo.
echo 💡 关于重新组织仓库结构的建议:
echo.
echo 🔄 方案1: 保持当前结构 (推荐)
echo   - ERL/ 和 pderl/ 作为两个独立的算法实现
echo   - 便于比较和独立开发
echo   - 符合比较研究的目的
echo.
echo 🔄 方案2: 标准化命名
echo   - 将 pderl/ 重命名为 PDERL/ (需要手动操作)
echo   - 统一大写命名风格
echo.
echo 🔄 方案3: 完全重构
echo   - 创建 algorithms/ERL/ 和 algorithms/PDERL/
echo   - 添加 experiments/, docs/, scripts/ 等目录
echo   - 更适合大型研究项目
echo.
echo 📝 下一步操作建议:
echo 1. 在GitHub上完善仓库描述和标签
echo 2. 添加实验结果和性能对比
echo 3. 完善README文档
echo 4. 考虑添加GitHub Actions自动化测试
echo.
pause
