#!/bin/bash
# 大领导系统 - 统一启动脚本
# 作者: 大领导系统 v5.16.0
# 日期: 2026-03-16
#
# 功能：一键启动所有监控面板

set -e

echo "🚀 大领导系统 - 统一启动"
echo "================================"

# 1. 检查 Gateway 状态
echo ""
echo "1️⃣ 检查 Gateway 状态..."
if systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
    echo "✅ Gateway 运行正常"
else
    echo "⚠️ Gateway 未运行，启动中..."
    systemctl --user start openclaw-gateway
    sleep 5
fi

# 2. 启动 Control Center
echo ""
echo "2️⃣ 启动 Control Center..."
if lsof -i :4310 >/dev/null 2>&1; then
    echo "✅ Control Center 已经在运行"
else
    echo "🚀 启动 Control Center..."
    bash /root/.openclaw/control-center/auto-start.sh
fi

# 3. 启动 AI Team Dashboard
echo ""
echo "3️⃣ 启动 AI Team Dashboard..."
if docker ps | grep -q "ai-team-"; then
    echo "✅ AI Team Dashboard 已经在运行"
else
    echo "🚀 启动 AI Team Dashboard..."
    bash /root/.openclaw/workspace/ai-team-dashboard/auto-start.sh
fi

echo ""
echo "================================"
echo "✅ 所有服务启动完成！"
echo ""
echo "📊 服务状态:"
echo "  - Gateway: http://43.134.63.176:18789 (飞书集成)"
echo "  - Control Center: http://43.134.63.176:4310 (监控面板)"
echo "  - AI Team Dashboard: http://43.134.63.176:3800 (AI 团队)"
echo ""
echo "💡 提示:"
echo "  - Gateway 是核心服务，必须运行"
echo "  - Control Center 和 AI Team Dashboard 是可选的监控面板"
echo ""
echo "🔧 管理命令:"
echo "  - 查看日志: journalctl --user -u openclaw-gateway -f"
echo "  - 重启服务: systemctl --user restart openclaw-gateway"
echo "  - 停止所有: pkill -f 'control-center|ai-team'"
