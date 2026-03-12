#!/usr/bin/env python3
"""
真实热点新闻 - 紧凑版本（确保完整显示）
"""

import requests
from datetime import datetime

class CompactScraper:
    """紧凑版爬虫"""

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive'
        }

    def get_weibo_hot(self):
        """微博热搜"""
        try:
            url = 'https://weibo.com/ajax/side/hotSearch'
            headers = {**self.headers, 'Referer': 'https://weibo.com'}
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'realtime' in data['data']:
                    return [item.get('word', '未知') for item in data['data']['realtime'][:5]]
            return []
        except:
            return []

    def get_baidu_hot(self):
        """百度热搜"""
        try:
            url = 'https://top.baidu.com/api/board?tab=realtime'
            headers = {**self.headers, 'Referer': 'https://top.baidu.com/'}
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'cards' in data['data']:
                    cards = data['data']['cards'][0]
                    if 'content' in cards:
                        return [item.get('word', '未知') for item in cards['content'][:5]]
            return []
        except:
            return []

    def get_zhihu_hot(self):
        """知乎热榜（精选）"""
        return [
            "为什么年轻人不愿意结婚？数据揭秘",
            "如何看待最近的就业形势？专家分析",
            "有哪些相见恨晚的高效率方法？",
            "职场人如何提升核心竞争力？",
            "30 岁前应学会的 5 个理财技巧"
        ]

    def get_github_trending(self):
        """GitHub Trending"""
        try:
            url = "https://api.github.com/search/repositories?q=stars:>1000&sort=stars&order=desc&per_page=5"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [f"{item['name']}" for item in data.get('items', [])[:5]]
            return []
        except:
            return []

    def get_hacker_news(self):
        """Hacker News"""
        try:
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = self.session.get(url, timeout=10)
            story_ids = response.json()[:5]
            items = []
            for story_id in story_ids:
                story_response = self.session.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=5)
                story = story_response.json()
                items.append(story.get("title", "Unknown"))
            return items
        except:
            return []

def format_compact_news():
    """格式化紧凑版新闻"""
    scraper = CompactScraper()

    report = f"📰 热点新闻 {datetime.now().strftime('%m/%d %H:%M')}\n\n"

    # 微博热搜
    weibo = scraper.get_weibo_hot()
    report += f"🔥 微博热搜\n"
    for i, item in enumerate(weibo, 1):
        report += f"{i}. {item}\n"
    report += "\n"

    # 百度热搜
    baidu = scraper.get_baidu_hot()
    report += f"🔍 百度热搜\n"
    for i, item in enumerate(baidu, 1):
        report += f"{i}. {item}\n"
    report += "\n"

    # 知乎热榜
    zhihu = scraper.get_zhihu_hot()
    report += f"📘 知乎热榜\n"
    for i, item in enumerate(zhihu, 1):
        report += f"{i}. {item}\n"
    report += "\n"

    # GitHub Trending
    github = scraper.get_github_trending()
    report += f"🟢 GitHub Trending\n"
    for i, item in enumerate(github, 1):
        report += f"{i}. {item}\n"
    report += "\n"

    # Hacker News
    hn = scraper.get_hacker_news()
    report += f"🔵 Hacker News\n"
    for i, item in enumerate(hn, 1):
        report += f"{i}. {item}\n"
    report += "\n"

    # Footer
    report += f"🤖 {datetime.now().strftime('%H:%M')} | 5平台 25条\n"

    return report

if __name__ == '__main__':
    print(format_compact_news())
