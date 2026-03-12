#!/bin/bash
# =============================================================================
# 🚀 股票分析系统 - 快速启动脚本
# =============================================================================

echo "📊 股票分析系统 - 启动脚本"
echo "======================================"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"
echo ""

# 安装依赖
echo "📦 安装依赖..."
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 依赖安装完成"
else
    echo "❌ 依赖安装失败"
    exit 1
fi

echo ""

# 创建必要的目录
echo "📁 创建数据目录..."
mkdir -p data/raw data/processed data/models

echo "✅ 目录创建完成"
echo ""

# 运行应用
echo "🚀 启动 Streamlit 应用..."
echo ""
echo "访问地址: http://localhost:8501"
echo "按 Ctrl+C 停止"
echo ""

streamlit run web/app.py
