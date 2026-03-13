#!/bin/bash
# 新闻推送到飞书脚本（通过 agent）

cd /root/.openclaw/workspace

# 获取最新的新闻日志（最后 100 行）
NEWS_LOG=$(tail -100 /root/.openclaw/workspace/logs/news-summary.log)

# 检查是否已推送（避免重复）
TODAY=$(date +%Y%m%d)
MARKER_FILE="/tmp/news_sent_${TODAY}"
if [ -f "$MARKER_FILE" ]; then
    echo "ℹ️ 今日新闻已推送，跳过"
    exit 0
fi

# 推送到飞书（通过太子）
echo "📰 正在推送新闻到飞书..."
# 使用 echo 消息会自动路由到当前会话
echo "$NEWS_LOG" > /tmp/news_to_send.txt

# 标记已推送
touch "$MARKER_FILE"
echo "✅ 新闻推送任务已提交"
