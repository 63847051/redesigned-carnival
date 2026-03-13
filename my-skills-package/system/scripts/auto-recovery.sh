#!/bin/bash
# 自动恢复脚本
# 在检测到我掉线时自动尝试恢复

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔄 自动恢复脚本启动..."
echo ""

# 检查 OpenClaw 进程
if pgrep -f "openclaw" > /dev/null; then
    echo "✅ OpenClaw 运行正常"
else
    echo "⚠️ OpenClaw 未运行，尝试启动..."
    
    # 尝试启动 Gateway
    systemctl --user start openclaw-gateway
    sleep 5
    
    if systemctl --user is-active --quiet openclaw-gateway; then
        echo "✅ Gateway 已恢复"
    else
        echo "❌ Gateway 启动失败"
        echo "请手动检查："
        echo "  systemctl --user status openclaw-gateway"
        exit 1
    fi
fi

echo ""
echo "✅ 自动恢复完成"
