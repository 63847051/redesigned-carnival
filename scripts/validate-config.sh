#!/bin/bash
# OpenClaw 配置验证脚本
# 作者: 大领导系统 v5.16.0
# 日期: 2026-03-16
#
# 用法: ./validate-config.sh
#
# 功能: 在修改配置前验证字段是否在 OpenClaw Schema 中

set -e

echo "🔍 OpenClaw 配置验证脚本"
echo "================================"

# 检查 openclaw.json 是否存在
CONFIG_FILE="/root/.openclaw/openclaw.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

echo "✅ 配置文件找到: $CONFIG_FILE"
echo ""

# 验证 JSON 格式
echo "1️⃣ 验证 JSON 格式..."
if python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
    echo "✅ JSON 格式正确"
else
    echo "❌ JSON 格式错误"
    echo "请运行: python3 -m json.tool $CONFIG_FILE"
    exit 1
fi
echo ""

# 检查 Gateway 当前状态
echo "2️⃣ 检查 Gateway 状态..."
if systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
    echo "✅ Gateway 运行正常"
    echo ""
    echo "最近 5 分钟错误："
    journalctl --user -u openclaw-gateway --since "5 minutes ago" --no-pager | grep -i "error\|invalid\|unrecognized" | tail -5 || echo "  无错误"
else
    echo "⚠️ Gateway 未运行"
fi
echo ""

# 已知的无效字段列表
echo "3️⃣ 检查已知无效字段..."
INVALID_FIELDS=(
    "context"
    "context.excludeFiles"
)

# 检查配置中是否包含无效字段
for field in "${INVALID_FIELDS[@]}"; do
    if grep -q "\"$field\"" "$CONFIG_FILE" 2>/dev/null; then
        echo "❌ 发现无效字段: \"$field\""
        echo ""
        echo "💡 建议:"
        echo "   1. 移除这个字段"
        echo "   2. 查阅 OpenClaw 文档确认支持的字段"
        echo ""
        echo "📖 参考:"
        echo "   - https://docs.openclaw.ai/gateway/configuration-reference"
        echo "   - https://docs.openclaw.ai/tools/subagents"
        echo ""
        echo "🔧 快速修复:"
        echo "   sed -i 's/\"$field\".*//' $CONFIG_FILE"
    else
        echo "✅ 未发现无效字段: \"$field\""
    fi
done

echo ""
echo "================================"
echo "✅ 验证完成！"
echo ""
echo "💡 使用建议:"
echo "1. 修改配置前先运行此脚本验证"
echo "2. 如果 Gateway 崩溃，检查日志: journalctl --user -u openclaw-gateway --since '10 minutes ago'"
echo "3. 查阅文档: https://docs.openclaw.ai/gateway/configuration-reference"
