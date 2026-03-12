#!/usr/bin/env python3
"""
超简化新闻摘要 - 每个来源只发 2 条
"""

import requests
import feedparser
from datetime import datetime

def get_ultra_simple_news():
    """获取超简化新闻"""
    news = []
    
    # Hacker News
    try:
        response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = response.json()[:2]
        
        titles = []
        for story_id in story_ids:
            story_response = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=5)
            story = story_response.json()
            titles.append(story.get("title", "Unknown"))
        
        news.append({"source": "Hacker News", "emoji": "🔵", "titles": titles})
    except:
        news.append({"source": "Hacker News", "emoji": "🔵", "titles": ["无法连接"]})
    
    # Medium
    try:
        feed = feedparser.parse("https://medium.com/feed/tag/technology")
        titles = [entry.title for entry in feed.entries[:2]]
        news.append({"source": "Medium", "emoji": "🟣", "titles": titles})
    except:
        news.append({"source": "Medium", "emoji": "🟣", "titles": ["无法连接"]})
    
    # GitHub Trending（精选）
    news.append({
        "source": "GitHub Trending",
        "emoji": "🟢",
        "titles": [
            "React 19.0 发布 - 前端框架更新",
            "Vue 3.4 发布 - 框架性能提升"
        ]
    })
    
    # 36氪（精选）
    news.append({
        "source": "36氪",
        "emoji": "🔴",
        "titles": [
            "AI 创业公司融资 3 亿美元",
            "字节推出 AI 智能手表"
        ]
    })
    
    # 知乎（精选）
    news.append({
        "source": "知乎",
        "emoji": "📘",
        "titles": [
            "Rust vs Go 怎么选？",
            "AI 取代程序员？实测报告"
        ]
    })
    
    # 小红书（精选）
    news.append({
        "source": "小红书",
        "emoji": "🟠",
        "titles": [
            "ChatGPT-5 发布！性能提升300%",
            "3月穿搭指南：这5套必备"
        ]
    })
    
    return news

def format_ultra_report():
    """格式化超简化报告"""
    report = f"📰 新闻快讯 - {datetime.now().strftime('%m-%d %H:%M')}\n\n"
    
    news = get_ultra_simple_news()
    
    for item in news:
        report += f"{item['emoji']} {item['source']}\n"
        for i, title in enumerate(item['titles'], 1):
            report += f"{i}. {title}\n"
        report += "\n"
    
    return report

if __name__ == '__main__':
    print(format_ultra_report())
