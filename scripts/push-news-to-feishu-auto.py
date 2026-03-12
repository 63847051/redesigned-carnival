#!/usr/bin/env python3
"""
自动推送新闻到飞书（通过 message 工具）
"""
import subprocess
import pathlib
from datetime import datetime

# 读取最新新闻
log_file = pathlib.Path("/root/.openclaw/workspace/logs/news-summary.log")
news_content = log_file.read_text().split("📰 真实热点新闻")[-1].split("🤖 AI 生成时间")[0]

# 构建消息
message = f"""📰 早朝简报 - {datetime.now().strftime('%Y年%m月%d日')}

{news_content}

────────────────────────
🤖 采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
📊 数据来源: 5个平台，共25条热点"""

# 写入临时文件
temp_file = pathlib.Path("/tmp/news_to_send.txt")
temp_file.write_text(message)

print(f"✅ 新闻已准备，等待推送...")
print(f"📊 消息长度: {len(message)} 字符")
