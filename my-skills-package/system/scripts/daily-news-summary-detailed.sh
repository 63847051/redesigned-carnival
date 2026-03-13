#!/bin/bash
# 每日新闻摘要脚本 - 超详细版（含飞书推送）
# 使用 hot-news-with-content.py 脚本生成新闻并推送到飞书

cd /root/.openclaw/workspace

# 1. 采集新闻
echo "📰 开始采集新闻..."
python3 /root/.openclaw/workspace/scripts/detailed-news-ultra.py >> /root/.openclaw/workspace/logs/news-summary.log 2>&1

# 2. 推送到飞书
echo "📤 开始推送到飞书..."
bash /root/.openclaw/workspace/scripts/push-news-to-feishu.sh

echo "✅ 新闻采集和推送完成"
