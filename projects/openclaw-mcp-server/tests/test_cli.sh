#!/bin/bash
# OpenClaw MCP Server 测试脚本 v2.0

echo "🧪 OpenClaw MCP Server v2.0 测试"
echo "================================"
echo ""

# 测试 openclaw 命令
echo "📋 测试 openclaw 命令..."
which openclaw
openclaw --version
echo ""

# 测试列出会话
echo "📊 测试 sessions list..."
openclaw sessions list --limit 5 2>&1 | head -20
echo ""

# 测试获取历史
echo "📜 测试 sessions history..."
openclaw sessions history "agent:main:feishu:default" --limit 3 2>&1 | head -20
echo ""

# 测试发送消息
echo "📤 测试 sessions send..."
echo "是否要发送测试消息？(y/n)"
read -r answer

if [ "$answer" = "y" ]; then
    openclaw sessions send --label main "MCP Server 测试消息"
fi

echo ""
echo "✅ 测试完成"
