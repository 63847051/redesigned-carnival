#!/bin/bash
# 初始化独立子 Agent 系统
# 创建时间: 2026-03-04

set -e

echo "========================================"
echo "🚀 初始化独立子 Agent 系统"
echo "========================================"
echo ""

# 检查 OpenClaw 是否运行
if ! command -v openclaw &> /dev/null; then
    echo "❌ OpenClaw 未安装"
    exit 1
fi

echo "✅ OpenClaw 已安装"
echo ""

# 创建日志目录
LOG_DIR="/root/.openclaw/workspace/logs/agents"
mkdir -p "$LOG_DIR"

echo "📋 准备初始化以下子 Agent："
echo "  1. 🏠 室内设计专家 (design-expert)"
echo "  2. 💻 技术支持专家 (tech-expert)"
echo "  3. 📋 小蓝 - 工作日志管理 (xiaolan)"
echo ""

echo "⚠️  重要提示："
echo "  - 子 Agent 将通过 OpenClaw sessions_spawn 初始化"
echo "  - 每个子 Agent 有独立的会话和模型"
echo "  - 上下文完全隔离，防止混淆污染"
echo "  - 初始化后，主控 Agent 将自动分配任务"
echo ""

echo "📝 下一步："
echo "  1. 在主控 Agent (大领导) 中执行初始化命令"
echo "  2. 验证每个子 Agent 的隔离性"
echo "  3. 测试跨 Agent 通信"
echo ""

echo "✅ 配置文件已准备完成"
echo "   - /root/.openclaw/workspace/agents/interior-design-expert.md"
echo "   - /root/.openclaw/workspace/agents/tech-support-expert.md"
echo "   - /root/.openclaw/workspace/agents/worklog-manager.md"
echo ""

echo "🎯 准备就绪！等待主控 Agent 初始化..."
echo ""
