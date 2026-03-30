#!/usr/bin/env python3
# 读取小红书笔记

import requests
from bs4 import BeautifulSoup
import sys

def read_xiaohongshu(url):
    """读取小红书笔记内容"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 尝试多种方式提取内容
        content_div = soup.find('div', class_='note-text')
        if not content_div:
            content_div = soup.find('div', {'id': 'note-content'})
        if not content_div:
            content_div = soup.find('div', class_='content')
        if not content_div:
            content_div = soup.find('article')

        if content_div:
            # 提取标题
            title_div = soup.find('h1') or soup.find('title')
            title = title_div.get_text().strip() if title_div else "无标题"

            # 提取内容
            text = content_div.get_text('\n', strip=True)

            print(f"✅ 成功读取笔记")
            print(f"📝 标题: {title}")
            print(f"📄 内容长度: {len(text)} 字符")
            print("=" * 50)
            print(text)
            print("=" * 50)

            return text
        else:
            print("❌ 未找到笔记内容")
            return None

    except Exception as e:
        print(f"❌ 读取失败: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 read-xiaohongshu.py <小红书笔记URL>")
        sys.exit(1)

    url = sys.argv[1]
    read_xiaohongshu(url)
