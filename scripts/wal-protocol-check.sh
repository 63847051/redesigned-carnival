#!/bin/bash
# WAL 协议检查脚本
# 检查用户消息是否包含关键信息，强制先写入再回复

USER_MESSAGE="$1"

# 关键信息关键词
KEYWORDS="纠正|决策|偏好|重要|记住|记录|更新|修改"

# 检查是否包含关键信息
if echo "$USER_MESSAGE" | grep -qE "$KEYWORDS"; then
    # 包含关键信息，强制写入 SESSION-STATE.md
    echo "⚠️ 检测到关键信息，正在写入 SESSION-STATE.md..."

    # 追加到 SESSION-STATE.md
    cat >> /root/.openclaw/workspace/SESSION-STATE.md << EOF

## 📝 [$(date +%Y-%m-%d\ %H:%M)] 用户消息

$USER_MESSAGE

EOF

    echo "✅ 已写入 SESSION-STATE.md"
fi
