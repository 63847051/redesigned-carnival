#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知乎专栏文章爬虫
使用 requests + BeautifulSoup 绕过知乎反爬虫
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re


def fetch_zhihu_article(url):
    """
    获取知乎专栏文章

    Args:
        url: 知乎专栏文章 URL

    Returns:
        文章内容（markdown 格式）
    """

    # iPhone User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    try:
        # 第一次请求，获取 HTML
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 检查是否是验证页面
        if '验证' in response.text or '验证码' in response.text:
            print("❌ 知乎需要验证，无法继续")
            return None

        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 尝试多种方式提取文章内容
        content = None

        # 方法 1: 查找 class="Post-RichText"
        post_rich = soup.find('div', class_='Post-RichText')
        if post_rich:
            content = post_rich.get_text('\n', strip=True)
            print("✅ 使用方法 1 提取成功（Post-RichText）")

        # 方法 2: 查找 class="RichText"
        if not content:
            rich_text = soup.find('div', class_='RichText')
            if rich_text:
                content = rich_text.get_text('\n', strip=True)
                print("✅ 使用方法 2 提取成功（RichText）")

        # 方法 3: 查找 article 标签
        if not content:
            article = soup.find('article')
            if article:
                content = article.get_text('\n', strip=True)
                print("✅ 使用方法 3 提取成功（article）")

        # 方法 4: 查找 script 标签中的 JSON 数据
        if not content:
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if 'article' in data or 'content' in data:
                        content = data.get('article', data.get('content', ''))
                        if isinstance(content, dict):
                            content = content.get('content', str(content))
                        print("✅ 使用方法 4 提取成功（JSON）")
                        break
                except:
                    continue

        if not content:
            print("❌ 无法提取文章内容")
            return None

        # 提取标题
        title = None
        title_tag = soup.find('h1', class_='Post-Title')
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            # 尝试从 script 中提取
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if 'title' in data:
                        title = data['title']
                        break
                except:
                    continue

        # 组装结果
        result = f"# {title or '未知标题'}\n\n"
        result += content

        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return None


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("用法: python zhihu_fetcher.py <知乎文章URL>")
        sys.exit(1)

    url = sys.argv[1]
    article = fetch_zhihu_article(url)

    if article:
        print(article)
    else:
        print("❌ 获取文章失败")
        sys.exit(1)
