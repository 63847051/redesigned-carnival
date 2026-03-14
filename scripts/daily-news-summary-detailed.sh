#!/bin/bash
# 每日新闻摘要脚本 - 真实热点 + AI 摘要版（含飞书推送）
# 使用 real-hot-news-with-ai-summary.py 脚本生成新闻并推送到飞书

cd /root/.openclaw/workspace

# 1. 采集新闻（使用真实爬虫 + AI 摘要）
echo "📰 开始采集真实热点新闻 + AI 摘要生成..."
python3 /root/.openclaw/workspace/scripts/real-hot-news-with-ai-summary.py > /tmp/latest_real_news.txt

# 2. 推送到飞书
echo "📤 开始推送到飞书..."
bash /root/.openclaw/workspace/scripts/push-news-to-feishu.sh

echo "✅ 新闻采集和推送完成"
