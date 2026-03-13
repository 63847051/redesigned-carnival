#!/bin/bash
# 关键规则检查 - 自主进化系统 5.9

WORKSPACE="/root/.openclaw/workspace"

echo "🚨 关键规则检查"
echo "================"
echo ""

# 检查 RULE-001
echo "🔍 检查 RULE-001: 重要操作必须等待确认"
if [ -f "$WORKSPACE/.learnings/rules/critical-rule-001-wait-confirmation.md" ]; then
    echo "✅ RULE-001 文件存在"
    echo ""
    cat "$WORKSPACE/.learnings/rules/critical-rule-001-wait-confirmation.md" | grep -A 5 "规则内容" || true
else
    echo "❌ RULE-001 文件缺失"
    exit 1
fi

echo ""
echo "---"
echo ""

# 检查 RULE-002
echo "🔍 检查 RULE-002: 版本号跟踪"
if [ -f "$WORKSPACE/.learnings/rules/critical-rule-002-version-tracking.md" ]; then
    echo "✅ RULE-002 文件存在"
    echo "   状态: 已激活"
    echo "   要求: 每次升级后必须更新版本号"
else
    echo "❌ RULE-002 文件缺失"
    exit 1
fi

echo ""
echo "================"
echo "✅ 所有关键规则检查通过"
