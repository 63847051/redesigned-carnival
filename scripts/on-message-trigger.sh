#!/bin/bash
# on_message 触发器监听脚本
# 作者: 大领导系统 v5.16.0
# 基于 Clawith 的 Aware 机制
#
# 用法: ./on-message-trigger.sh <message_source> <trigger_action>
#
# 示例: ./on-message-trigger.sh "user:ou_xxx" "执行任务"

set -e

MESSAGE_SOURCE=$1
TRIGGER_ACTION=$2

if [ -z "$MESSAGE_SOURCE" ] || [ -z "$TRIGGER_ACTION" ]; then
    echo "❌ 错误: 缺少参数"
    echo "用法: $0 <message_source> <trigger_action>"
    echo ""
    echo "示例:"
    echo "  $0 \"user:ou_xxx\" \"执行任务\""
    echo "  $0 \"agent:opencode\" \"继续执行\""
    exit 1
fi

echo "📨 on_message 触发器已启动"
echo "🎯 监听来源: $MESSAGE_SOURCE"
echo "⚡ 触发动作: $TRIGGER_ACTION"
echo ""

# 解析消息来源
SOURCE_TYPE=$(echo "$MESSAGE_SOURCE" | cut -d: -f1)
SOURCE_ID=$(echo "$MESSAGE_SOURCE" | cut -d: -f2)

case $SOURCE_TYPE in
  user)
    echo "👤 监听用户消息: $SOURCE_ID"
    ;;
  agent)
    echo "🤖 监听 Agent 消息: $SOURCE_ID"
    ;;
  *)
    echo "❌ 错误: 无效的消息来源类型"
    echo "支持的类型: user, agent"
    exit 1
esac

echo ""
echo "🔄 开始监听..."
echo "💡 按 Ctrl+C 停止监听"
echo ""

# 模拟监听循环（实际实现需要使用 OpenClaw API）
while true; do
    # 检查是否有新消息
    # 这里需要实际的 API 调用来检查消息
    
    # 临时方案：每 10 秒检查一次
    sleep 10
    
    # 模拟：如果有新消息
    # echo "🔔 收到新消息，执行触发动作"
    # eval "$TRIGGER_ACTION"
    
    # 实际实现应该是：
    # 1. 使用 OpenClaw 的 sessions_list API
    # 2. 检查是否有来自特定来源的新消息
    # 3. 如果有，执行 TRIGGER_ACTION
    # 4. 继续监听
    
    echo "[$(date '+%H:%M:%S')] 💤 等待消息..."
done

echo ""
echo "================================"
echo "⚠️ 注意: 这是一个演示脚本"
echo ""
echo "📋 实际实现需要:"
echo "   1. 使用 OpenClaw 的 sessions_list API"
echo "   2. 检查来自特定来源的消息"
echo "   3. 触发后执行动作"
echo ""
echo "💡 推荐方式:"
echo "   - 使用 OpenClaw 的原生消息路由"
echo "   - 在 AGENTS.md 中定义触发规则"
echo "   - 利用 Gateway 的自动路由机制"
