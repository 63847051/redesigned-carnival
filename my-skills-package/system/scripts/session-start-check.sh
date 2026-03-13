#!/bin/bash
# 会话启动 - 关键规则检查
# 自主进化系统 5.7

echo "🚨 会话启动 - 关键规则检查"
echo "================================"
echo ""
bash /root/.openclaw/workspace/scripts/check-critical-rules.sh
echo ""
echo "✅ 会话启动完成"
echo "⚠️  重要操作前必须等待用户确认！"
echo ""
