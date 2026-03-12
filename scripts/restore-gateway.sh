#!/bin/bash
# Gateway 恢复脚本 - 如果重启失败使用

echo "🚨 Gateway 恢复模式"
echo "================================"
echo ""

# 查找最新的备份
LATEST_BACKUP=$(ls -t ~/.openclaw/openclaw.json.pre-restart-* 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ 未找到备份文件!"
    exit 1
fi

echo "📁 找到备份: $LATEST_BACKUP"
echo ""

# 恢复配置
echo "🔄 恢复配置文件..."
cp "$LATEST_BACKUP" ~/.openclaw/openclaw.json
echo "✅ 配置已恢复"
echo ""

# 重启 Gateway
echo "🔄 重启 Gateway..."
openclaw gateway restart

echo ""
echo "✅ 恢复完成!"
echo ""
echo "验证状态:"
openclaw gateway status
