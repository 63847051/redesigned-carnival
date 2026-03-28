#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知乎专栏文章列表获取工具
"""

import requests
import json


def get_column_articles(column_id):
    """
    获取知乎专栏文章列表

    Args:
        column_id: 专栏 ID（从 URL 中提取）

    Returns:
        文章列表
    """

    # 知乎专栏 API
    api_url = f"https://www.zhihu.com/api/v4/columns/{column_id}/items"

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Referer': 'https://www.zhihu.com/',
    }

    params = {
        'limit': 10,
        'offset': 0,
    }

    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # 提取文章列表
        articles = []
        for item in data.get('data', []):
            article = {
                'title': item.get('title', '未知标题'),
                'article_id': item.get('id', ''),
                'url': f"https://zhuanlan.zhihu.com/p/{item.get('id', '')}",
                'created': item.get('created', 0),
                'excerpt': item.get('excerpt', '')[:100],
            }
            articles.append(article)

        return articles

    except Exception as e:
        print(f"❌ 获取文章列表失败: {e}")
        return []


def extract_column_id(url):
    """
    从 URL 中提取专栏 ID

    Args:
        url: 知乎专栏 URL

    Returns:
        专栏 ID
    """

    # 专栏 URL: https://www.zhihu.com/column/c_1382759191564603392
    if '/column/c_' in url:
        return url.split('/column/c_')[-1].split('?')[0]
    else:
        print("❌ 无法从 URL 中提取专栏 ID")
        return None


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("用法: python zhihu-column.py <知乎专栏URL>")
        print("示例: python zhihu-column.py https://www.zhihu.com/column/c_1382759191564603392")
        sys.exit(1)

    url = sys.argv[1]
    column_id = extract_column_id(url)

    if column_id:
        articles = get_column_articles(column_id)

        if articles:
            print(f"✅ 找到 {len(articles)} 篇文章:\n")
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article['title']}")
                print(f"   URL: {article['url']}")
                print(f"   摘要: {article['excerpt']}")
                print()
        else:
            print("❌ 获取文章列表失败")
            sys.exit(1)
    else:
        sys.exit(1)
