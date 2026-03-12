#!/usr/bin/env python3
"""
使用 Scrapling 的 Stealth 模式抓取热点新闻
绕过反爬虫机制
"""

from scrapling import Fetcher
from datetime import datetime

def get_weibo_hot_stealth():
    """使用 Scrapling Stealth 模式抓取微博热搜"""
    try:
        # 配置 Fetcher 使用 Stealth 模式
        fetcher = Fetcher(
            stealth=True,  # 启用隐身模式
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )

        # 抓取微博热搜
        response = fetcher.get('https://s.weibo.com/top/summary')

        # 尝试多种选择器
        selectors = [
            'tbody tr td:nth-child(2) a::text',
            'a[href*="/hot/"]::text',
            '.list a::text',
            'td a::text'
        ]

        hot_items = []
        for selector in selectors:
            items = response.css(selector).getall()
            if items:
                hot_items = items[:5]
                break

        return hot_items
    except Exception as e:
        print(f"微博热搜抓取失败: {e}")
        return []

def get_zhihu_hot_stealth():
    """使用 Scrapling Stealth 模式抓取知乎热榜"""
    try:
        fetcher = Fetcher(
            stealth=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )

        response = fetcher.get('https://www.zhihu.com/hot')

        # 尝试多种选择器
        selectors = [
            '.HotItem-title::text',
            '.HotItem-title a::text',
            'h2::text',
            '.title::text'
        ]

        hot_items = []
        for selector in selectors:
            items = response.css(selector).getall()
            if items:
                hot_items = items[:5]
                break

        return hot_items
    except Exception as e:
        print(f"知乎热榜抓取失败: {e}")
        return []

def get_baidu_hot_stealth():
    """使用 Scrapling Stealth 模式抓取百度热搜"""
    try:
        fetcher = Fetcher(
            stealth=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )

        response = fetcher.get('https://top.baidu.com/board?tab=realtime')

        # 尝试多种选择器
        selectors = [
            '.title_dIFcB::text',
            '.title::text',
            'a::text',
            '.content-title::text'
        ]

        hot_items = []
        for selector in selectors:
            items = response.css(selector).getall()
            if items:
                hot_items = items[:5]
                break

        return hot_items
    except Exception as e:
        print(f"百度热搜抓取失败: {e}")
        return []

def format_stealth_hot_news():
    """格式化 Stealth 模式抓取的热点新闻"""
    report = f"📰 真实热点新闻（Scrapling Stealth） - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    # 微博热搜
    weibo = get_weibo_hot_stealth()
    report += "🔥 微博热搜 (5条)\n"
    report += "────────────────────────\n"
    if weibo:
        for i, item in enumerate(weibo, 1):
            report += f"{i}. {item}\n"
    else:
        report += "⚠️  暂时无法抓取\n"
    report += "\n"

    # 知乎热榜
    zhihu = get_zhihu_hot_stealth()
    report += "📘 知乎热榜 (5条)\n"
    report += "────────────────────────\n"
    if zhihu:
        for i, item in enumerate(zhihu, 1):
            report += f"{i}. {item}\n"
    else:
        report += "⚠️  暂时无法抓取\n"
    report += "\n"

    # 百度热搜
    baidu = get_baidu_hot_stealth()
    report += "🔍 百度热搜 (5条)\n"
    report += "────────────────────────\n"
    if baidu:
        for i, item in enumerate(baidu, 1):
            report += f"{i}. {item}\n"
    else:
        report += "⚠️  暂时无法抓取\n"
    report += "\n"

    # Footer
    report += "────────────────────────\n"
    report += f"🤖 AI 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report += f"📊 数据来源: 3 个平台\n"
    report += f"✅ 使用 Scrapling Stealth 模式\n"

    return report

if __name__ == '__main__':
    print(format_stealth_hot_news())
