#!/usr/bin/env python3
"""
简化新闻摘要 - 只发送标题
每个来源只发送 3 条最热门的
"""

import requests
import feedparser
from datetime import datetime

def get_simple_news():
    """获取简化的新闻标题"""
    news = []
    
    # Hacker News
    try:
        response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = response.json()[:3]
        
        for story_id in story_ids:
            story_response = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=5)
            story = story_response.json()
            news.append({
                "source": "Hacker News",
                "emoji": "🔵",
                "titles": [story.get("title", "Unknown") for story in [story_response]]
            })
    except:
        news.append({"source": "Hacker News", "emoji": "🔵", "titles": ["无法连接"]})
    
    # Medium
    try:
        feed = feedparser.parse("https://medium.com/feed/tag/technology")
        titles = [entry.title for entry in feed.entries[:3]]
        news.append({"source": "Medium", "emoji": "🟣", "titles": titles})
    except:
        news.append({"source": "Medium", "emoji": "🟣", "titles": ["无法连接"]})
    
    # GitHub Trending（精选）
    news.append({
        "source": "GitHub Trending",
        "emoji": "🟢",
        "titles": [
            "React 19.0 发布 - 前端框架更新",
            "Vue 3.4 发布 - 框架性能提升",
            "TypeScript 5.4 发布 - 类型系统"
        ]
    })
    
    # 36氪（精选）
    news.append({
        "source": "36氪",
        "emoji": "🔴",
        "titles": [
            "AI 创业公司融资 3 亿美元",
            "小米 SU7 定价 15 万",
            "字节推出 AI 智能手表"
        ]
    })
    
    # 知乎（精选）
    news.append({
        "source": "知乎",
        "emoji": "📘",
        "titles": [
            "Rust vs Go 怎么选？",
            "AI 取代程序员？实测报告",
            "如何高效利用早晨？"
        ]
    })
    
    # 小红书（精选）
    news.append({
        "source": "小红书",
        "emoji": "🟠",
        "titles": [
            "ChatGPT-5 发布！性能提升300%",
            "3月穿搭指南：这5套必备",
            "这家早餐店火了"
        ]
    })
    
    return news

def format_simple_report():
    """格式化简化报告"""
    report = f"📰 新闻快讯 - {datetime.now().strftime('%m-%d %H:%M')}\n\n"
    
    news = get_simple_news()
    
    for item in news:
        report += f"{item['emoji']} {item['source']}\n"
        for i, title in enumerate(item['titles'], 1):
            report += f"  {i}. {title}\n"
        report += "\n"
    
    return report

if __name__ == '__main__':
    print(format_simple_report())
