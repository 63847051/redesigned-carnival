#!/bin/bash
# 大领导在群里调用"编程小幸运"
# 用法: bash mention-opencode-in-group.sh "群聊ID" "任务描述"

CHAT_ID="$1"
TASK="$2"

if [ -z "$CHAT_ID" ] || [ -z "$TASK" ]; then
  echo "❌ 用法: bash mention-opencode-in-group.sh \"群聊ID\" \"任务描述\""
  echo "📋 当前群聊ID: oc_65a1c1459bcf9126ad362bffac588e34"
  exit 1
fi

echo "🎯 大领导正在群里@编程小幸运..."
echo "💬 群聊: $CHAT_ID"
echo "📋 任务: $TASK"

# 使用飞书 API 发送消息
# 注意: 这需要使用 opencode 账号的凭证
echo "⏳ 需要使用飞书 API 发送@消息..."
echo "💡 消息格式: @编程小幸运 $TASK"

# 记录任务
echo "$(date '+%Y-%m-%d %H:%M:%S') | $CHAT_ID | $TASK" >> /root/.openclaw/workspace/logs/opencode-tasks.log

echo "✅ 任务已记录到日志"
