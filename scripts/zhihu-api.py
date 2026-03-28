#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知乎文章获取工具（使用知乎 API）
"""

import requests
import json


def get_zhihu_article_by_api(article_id):
    """
    使用知乎 API 获取文章

    Args:
        article_id: 文章 ID（从 URL 中提取）

    Returns:
        文章内容
    """

    # 知乎 API 端点
    api_url = f"https://www.zhihu.com/api/v4/articles/{article_id}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Referer': 'https://www.zhihu.com/',
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        # 提取标题和内容
        title = data.get('title', '未知标题')
        content = data.get('content', '')
        author = data.get('author', {}).get('name', '未知作者')

        # 组装结果
        result = f"# {title}\n\n"
        result += f"作者: {author}\n\n"
        result += content

        return result

    except Exception as e:
        print(f"❌ API 请求失败: {e}")
        return None


def extract_article_id(url):
    """
    从 URL 中提取文章 ID

    Args:
        url: 知乎文章 URL

    Returns:
        文章 ID
    """

    # 专栏 URL: https://www.zhihu.com/column/c_1382759191564603392
    # 文章 URL: https://zhuanlan.zhihu.com/p/123456789

    # 尝试提取文章 ID
    if '/p/' in url:
        return url.split('/p/')[-1].split('?')[0]
    else:
        print("❌ 无法从 URL 中提取文章 ID")
        print("💡 请提供具体的文章 URL（如: https://zhuanlan.zhihu.com/p/123456789）")
        return None


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("用法: python zhihu-api.py <知乎文章URL>")
        print("示例: python zhihu-api.py https://zhuanlan.zhihu.com/p/123456789")
        sys.exit(1)

    url = sys.argv[1]
    article_id = extract_article_id(url)

    if article_id:
        article = get_zhihu_article_by_api(article_id)
        if article:
            print(article)
        else:
            print("❌ 获取文章失败")
            sys.exit(1)
    else:
        sys.exit(1)
