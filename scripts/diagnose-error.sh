#!/bin/bash
# OpenClaw 错误快速诊断脚本
# 作者: 大领导系统 v5.16.0
# 日期: 2026-03-16
#
# 用法: ./diagnose-error.sh
#
# 功能: 快速诊断 Gateway 错误，定位问题并提供修复建议

set -e

echo "🔍 OpenClaw 错误诊断脚本"
echo "================================"

# 检查 Gateway 状态
echo "1️⃣ 检查 Gateway 状态..."
if systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
    echo "✅ Gateway 运行正常"
    GATEWAY_RUNNING=true
else
    echo "❌ Gateway 未运行"
    GATEWAY_RUNNING=false
fi
echo ""

# 检查最近的错误日志
echo "2️⃣ 检查最近的错误日志..."
if [ "$GATEWAY_RUNNING" = true ]; then
    echo "最近 30 分钟的错误："
    ERROR_LOG=$(journalctl --user -u openclaw-gateway --since "30 minutes ago" --no-pager | grep -i "error\|invalid\|unrecognized\|crash" | tail -10)
    if [ -z "$ERROR_LOG" ]; then
        echo "  ✅ 无错误"
    else
        echo "$ERROR_LOG"
    fi
else
    echo "⚠️ Gateway 未运行，无法获取错误日志"
fi
echo ""

# 检查配置文件
echo "3️⃣ 检查配置文件..."
CONFIG_FILE="/root/.openclaw/openclaw.json"
if [ -f "$CONFIG_FILE" ]; then
    echo "✅ 配置文件存在: $CONFIG_FILE"

    # 检查 JSON 格式
    if python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
        echo "✅ JSON 格式正确"
        JSON_VALID=true
    else
        echo "❌ JSON 格式错误"
        echo "💡 修复建议:"
        echo "   python3 -m json.tool $CONFIG_FILE > /tmp/openclaw.json"
        echo "   mv /tmp/openclaw.json $CONFIG_FILE"
        JSON_VALID=false
    fi
else
    echo "❌ 配置文件不存在: $CONFIG_FILE"
    JSON_VALID=false
fi
echo ""

# 检查已知无效字段
echo "4️⃣ 检查已知无效字段..."
INVALID_FIELDS=(
    "context"
    "context.excludeFiles"
)

HAS_INVALID_FIELD=false
for field in "${INVALID_FIELDS[@]}"; do
    if [ -f "$CONFIG_FILE" ] && [ "$JSON_VALID" = true ]; then
        if grep -q "\"$field\"" "$CONFIG_FILE" 2>/dev/null; then
            echo "❌ 发现无效字段: \"$field\""
            HAS_INVALID_FIELD=true
        fi
    fi
done

if [ "$HAS_INVALID_FIELD" = false ]; then
    echo "✅ 未发现已知无效字段"
fi
echo ""

# 检查最近的配置修改
echo "5️⃣ 检查最近的配置修改..."
if [ -f "$CONFIG_FILE" ] && [ "$JSON_VALID" = true ]; then
    LAST_CHANGE=$(stat -c %y "$CONFIG_FILE" 2>/dev/null || echo "未知")
    echo "最后修改时间: $LAST_CHANGE"

    # 检查备份文件
    BACKUP_FILE=$(ls -t /root/.openclaw/openclaw.json.backup-* 2>/dev/null | head -1)
    if [ -n "$BACKUP_FILE" ]; then
        echo "最新备份: $BACKUP_FILE"
    fi
else
    echo "⚠️ 无法检查配置修改时间（配置文件损坏或不存在）"
fi
echo ""

# 提供修复建议
echo "6️⃣ 修复建议..."
if [ "$GATEWAY_RUNNING" = false ]; then
    echo "📝 建议：启动 Gateway"
    echo "   systemctl --user start openclaw-gateway"
elif [ "$JSON_VALID" = false ]; then
    echo "📝 建议：修复 JSON 格式"
    echo "   python3 -m json.tool $CONFIG_FILE > /tmp/openclaw.json"
    echo "   mv /tmp/openclaw.json $CONFIG_FILE"
elif [ "$HAS_INVALID_FIELD" = true ]; then
    echo "📝 建议：移除无效字段"
    echo "   # 使用 sed 或 vim 编辑器删除无效字段"
    echo "   # 或使用备份文件回滚"
    if [ -n "$BACKUP_FILE" ]; then
        echo "   cp $BACKUP_FILE $CONFIG_FILE && systemctl --user restart openclaw-gateway"
    fi
else
    echo "✅ 当前状态正常，无需修复"
fi

echo ""
echo "================================"
echo "✅ 诊断完成！"
echo ""
echo "💡 更多帮助:"
echo "   - 查看文档: https://docs.openclaw.ai/gateway/configuration-reference"
echo "   - 验证配置: ~/.openclaw/workspace/scripts/validate-config.sh"
echo "   - Gateway 日志: journalctl --user -u openclaw-gateway --since '30 minutes ago'"
