#!/bin/bash
# 微信公众号文章阅读器 MCP 服务器 - 启动脚本
#
# 版本: 1.0.0
# 创建时间: 202set-03-12

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_SCRIPT="$SCRIPT_DIR/server.py"
VENV_DIR="$SCRIPT_DIR/venv"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

echo "=================================================="
echo "🚀 启动微信公众号文章阅读器 MCP 服务器"
echo "=================================================="
echo ""

# 检查 Python 版本
echo "🔍 检查 Python 版本..."
python3 --version || {
    echo "❌ 需要 Python 3.10+"
    exit 1
}
echo "✅ Python 版本检查通过"
echo ""

# 创建虚拟环境
if [[ ! -d "$VENV_DIR" ]]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
    echo "✅ 虚拟环境已创建"
else
    echo "✅ 虚拟环境已存在"
fi
echo ""

# 安装依赖
echo "📦 安装依赖..."
source "$VENV_DIR/bin/activate"
pip install -r "$REQUIREMENTS" > /dev/null 2>&1
echo "✅ 依赖安装完成"
echo ""

# 启动服务器
echo "🚀 启动 MCP 服务器..."
echo "服务器地址: stdio"
echo "按 Ctrl+C 停止服务器"
echo ""

python3 server.py
