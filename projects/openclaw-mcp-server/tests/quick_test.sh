#!/bin/bash
# OpenClaw MCP Server 快速测试脚本

echo "🧪 OpenClaw MCP Server 快速测试"
echo "================================"
echo ""

# 检查 Python 版本
echo "📋 检查 Python 版本..."
python3 --version
echo ""

# 检查依赖
echo "📦 检查依赖..."
echo "mcp: $(python3 -c 'import mcp; print(mcp.__version__)' 2>/dev/null || echo '未安装')"
echo "httpx: $(python3 -c 'import httpx; print(httpx.__version__)' 2>/dev/null || echo '未安装')"
echo ""

# 测试 API 连接
echo "🔗 测试 Gateway 连接..."
GATEWAY_URL="http://localhost:18789"
curl -s -o /dev/null -w "HTTP 状态码: %{http_code}\n" "$GATEWAY_URL/api/sessions" 2>/dev/null || echo "⚠️ Gateway 未响应"
echo ""

# 测试发送消息
echo "📤 测试 send_message API..."
RESPONSE=$(curl -s -X POST "$GATEWAY_URL/api/sessions/send" \
  -H "Content-Type: application/json" \
  -d '{"sessionKey":"agent:main:test","message":"测试消息"}' 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ API 调用成功"
    echo "响应: $RESPONSE" | head -c 200
else
    echo "❌ API 调用失败"
fi
echo ""

echo "✅ 快速测试完成"
