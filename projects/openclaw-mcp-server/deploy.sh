#!/bin/bash
# MCP Server v2.5 部署脚本

set -e

echo "🚀 开始部署 MCP Server v2.5..."

# 1. 检查依赖
echo "📦 检查依赖..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

if ! command -v openclaw &> /dev/null; then
    echo "❌ OpenClaw 未安装"
    exit 1
fi

# 2. 安装 MCP Server
echo "📦 安装 MCP Server..."
cd /root/.openclaw/workspace/projects/openclaw-mcp-server
pip install -e . --quiet

# 3. 验证安装
echo "✅ 验证安装..."
python3 -c "import openclaw_mcp_server; print('✅ 模块导入成功')"

# 4. 测试工具
echo "🧪 测试工具..."
python3 -m openclaw_mcp_server &
PID=$!
sleep 2
kill $PID 2>/dev/null || true

# 5. 添加到 OpenClaw 配置
echo "⚙️ 配置 OpenClaw..."
# 这里需要手动配置，因为涉及到 JSON 编辑

echo ""
echo "✅ MCP Server v2.5 部署完成！"
echo ""
echo "📝 下一步："
echo "1. 手动添加到 OpenClaw 配置"
echo "2. 重启 OpenClaw Gateway"
echo "3. 测试工具功能"
echo ""
echo "🔧 配置示例："
echo 'mcp:'
echo '  servers:'
echo '    openclaw:'
echo '      command: python3'
echo '      args: [-m, openclaw_mcp_server]'
