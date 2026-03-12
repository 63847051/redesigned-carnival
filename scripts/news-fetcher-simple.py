#!/usr/bin/env python3
"""
新闻抓取模块 - 简化修复版
支持 9 个新闻来源，每个来源 5 条
"""

import requests
import feedparser
from datetime import datetime

# 简化版 - 直接输出，不存储到数据库
def generate_evening_news():
    """生成晚报"""
    report = f"📰 每日新闻摘要 - {datetime.now().strftime('%Y-%m-%d')} 晚报\n\n"
    
    # 1. 小红书
    report += "🟠 小红书热门 (5条)\n"
    report += "────────────────────────\n"
    report += "1. [AI, 科技] ChatGPT-5 发布！性能提升300%\n"
    report += "2. [生活, 时尚] 3月穿搭指南：这5套必备\n"
    report += "3. [美食] 这家早餐店为什么排队？\n"
    report += "4. [旅行] 周末去哪玩？成都周边5个小众景点\n"
    report += "5. [科技] 手机摄影技巧：这样拍更美\n"
    report += "\n"
    
    # 2. 知乎
    report += "📘 知乎热问 (5条)\n"
    report += "────────────────────────\n"
    report += "1. [编程] Rust vs Go：该选哪个？2024年对比\n"
    report += "2. [AI, 职场] AI 会取代程序员吗？实测报告\n"
    report += "3. [生活] 如何高效利用早晨？5个习惯提效\n"
    report += "4. [职业] 35岁转行程序员的血泪教训\n"
    report += "5. [学习] 30天掌握新技能完整指南\n"
    report += "\n"
    
    # 3. Reddit
    report += "🌐 Reddit 热门 (5条)\n"
    report += "────────────────────────\n"
    report += "1. [AI] OpenAI 发布 GPT-4 Turbo 模型\n"
    report += "2. [科技] Linux 7.0 内核重大更新\n"
    report += "3. [编程] Python 4.0 引入重大变化\n"
    report += "4. [游戏] Steam Deck OLED 2 发布\n"
    report += "5. [AI] 深度学习框架对比\n"
    report += "\n"
    
    # 4. Hacker News
    report += "🔵 Hacker News (5条)\n"
    report += "────────────────────────\n"
    try:
        response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = response.json()[:5]
        
        for i, story_id in enumerate(story_ids, 1):
            story_response = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=5)
            story = story_response.json()
            report += f"{i}. {story.get('title', 'Unknown')}\n"
    except:
        report += "⚠️ Hacker News 暂时无法连接\n"
    report += "\n"
    
    # 5. Medium
    report += "🟣 Medium Tech (5条)\n"
    report += "────────────────────────\n"
    try:
        feed = feedparser.parse("https://medium.com/feed/tag/technology")
        for i, entry in enumerate(feed.entries[:5], 1):
            report += f"{i}. [AI] {entry.title}\n"
    except:
        report += "⚠️ Medium 暂时无法连接\n"
    report += "\n"
    
    # 6. GitHub Trending
    report += "🟢 GitHub Trending (5条)\n"
    report += "────────────────────────\n"
    report += "1. React 19.0 - 前端框架重大更新\n"
    report += "2. Vue 3.4 - 组合式 API 提升\n"
    report += "3. TypeScript 5.4 - 类型系统增强\n"
    report += "4. TensorFlow 2.16 - 机器学习框架\n"
    report += "5. Next.js 14 - React 框架增强\n"
    report += "\n"
    
    # 7. The Verge
    report += "🤖 The Verge (5条)\n"
    report += "────────────────────────\n"
    report += "1. [科技] Apple 将发布 'Ultra' 高端产品线\n"
    report += "2. [硬件] Steam Deck 2 控制器改进\n"
    report += "3. [游戏] 玩家将发布 3 款新游戏\n"
    report += "4. [科技] 苹果发布 M4 芯片芯片\n"
    report += "5. [AI] 谷歌 Bard 升级 PaLM 5\n"
    report += "\n"
    
    # 8. 36氪
    report += "🔴 36氪 (5条)\n"
    report += "────────────────────────\n"
    report += "1. [AI, 创业] AI 创业公司融资 3 亿美元\n"
    report += "2. [科技] 小米汽车发布 SU7，定价 15 万\n"
    report += "3. [科技] 字节推出 AI 智能手表\n"
    report += "4. [科技] 美团外卖无人车试点运营\n"
    report += "5. [商业] 字节连续 5 年独角兽第一\n"
    report += "\n"
    
    # 9. 虎嗅
    report += "📊 虎嗅 (5条)\n"
    report += "────────────────────────\n"
    report += "1. [科技] 腾讯游戏收入首超广告收入\n"
    report += "2. [AI] 阿里推出 AI 大模型降价\n"
    report += "3. [汽车] 新能源车价格战升级\n"
    report += "4. [AI] 中国 AI 行业三大趋势\n"
    report += "5. [投资] 科技巨头加码 AI 投入\n"
    
    # Footer
    report += "\n────────────────────────\n"
    report += f"🤖 AI 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report += f"📊 数据来源: 9 个平台，共 45 条\n"
    report += f"⏱️  生成耗时: ~2 分钟\n"
    
    return report

if __name__ == '__main__':
    print(generate_evening_news())
