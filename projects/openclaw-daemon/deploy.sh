#!/bin/bash
# OpenClaw Daemon v1.2 部署脚本

set -e

echo "🚀 开始部署 OpenClaw Daemon v1.2..."

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

# 2. 创建必要目录
echo "📁 创建目录..."
mkdir -p /root/.openclaw/workspace
mkdir -p /var/log/openclaw

# 3. 测试启动
echo "🧪 测试启动..."
cd /root/.openclaw/workspace/projects/openclaw-daemon

# 后台启动（测试 5 秒）
timeout 5 python3 openclaw_daemon.py --test || true

echo ""
echo "✅ OpenClaw Daemon v1.2 准备完成！"
echo ""
echo "📝 使用方法："
echo "1. 启动服务: python3 openclaw_daemon.py"
echo "2. 后台运行: nohup python3 openclaw_daemon.py > /var/log/openclaw/daemon.log 2>&1 &"
echo "3. 查看状态: python3 openclaw_daemon.py --status"
echo "4. 停止服务: python3 openclaw_daemon.py --stop"
echo ""
echo "🔧 功能特性："
echo "- 3 种 Driver（Subagent、ACP、OpenCode）"
echo "- 自动重启优化"
echo "- 消息队列持久化"
echo "- 错误恢复机制"
echo "- 健康检查（30秒）"
echo "- 性能监控"
