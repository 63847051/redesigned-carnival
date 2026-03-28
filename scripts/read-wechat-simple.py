#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信文章读取工具（简化版）
使用 requests + BeautifulSoup
"""

import requests
from bs4 import BeautifulSoup
import sys


def read_wechat_article(url):
    """
    读取微信文章

    Args:
        url: 微信文章 URL

    Returns:
        文章内容
    """

    # iPhone User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取标题
        title = soup.find('h1')
        if title:
            title = title.get_text(strip=True)
        else:
            title = "未知标题"

        # 提取作者
        author = "未知作者"
        author_meta = soup.find('meta', {'property': 'og:article:author'})
        if author_meta:
            author = author_meta.get('content', '未知作者')

        # 提取内容
        content_div = soup.find('div', {'id': 'js_content'})
        if content_div:
            content = content_div.get_text('\n', strip=True)
        else:
            content = "无法提取内容"

        # 组装结果
        result = f"# {title}\n\n"
        result += f"**作者**: {author}\n\n"
        result += content

        return result

    except Exception as e:
        return f"❌ 读取失败: {e}"


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python read_wechat_simple.py <微信文章URL>")
        sys.exit(1)

    url = sys.argv[1]
    article = read_wechat_article(url)
    print(article)
