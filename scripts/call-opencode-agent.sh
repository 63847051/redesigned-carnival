#!/bin/bash
# 大领导调用"编程小幸运"的桥接脚本
# 用法: bash call-opencode-agent.sh "任务描述"

TASK="$1"

if [ -z "$TASK" ]; then
  echo "❌ 用法: bash call-opencode-agent.sh \"任务描述\""
  exit 1
fi

echo "🎯 大领导正在调用编程小幸运..."
echo "📋 任务: $TASK"

# 保存任务到临时文件
TASK_FILE="/tmp/opencode-task-$(date +%s).txt"
echo "$TASK" > "$TASK_FILE"

echo "✅ 任务已保存到: $TASK_FILE"
echo "💡 下一步: 需要配置飞书 API 来发送消息给编程小幸运"

# TODO: 集成飞书 API
# 使用 feishu_im_user_message 工具
# account_id: opencode
# 接收者: 编程小幸运的 open_id 或 chat_id

echo "⏳ 等待实现飞书 API 集成..."
