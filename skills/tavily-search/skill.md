#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tavily AI 搜索 Skill
为 OpenClaw 添加 AI 搜索能力
"""

import os
import requests
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# 从环境变量获取 API Key
TAVILY_API_KEY = os.getenv('TAVILYLY_API_KEY', '')

# API 端点
TAVILY_API_URL = "https://api.tavily.com/search"

# 默认配置
DEFAULT_CONFIG = {
    "search_depth": "basic",
    "max_results": 5,
    "include_raw_content": False,
    "include_answer": False,
}

# 搜索深度选项
SEARCH_DEPTHS = {
    "basic": "快速搜索（3 个结果）",
    "advanced": "深度搜索（10 个结果）",
    "comprehensive": "全面搜索（15 个结果）",
}

# 实战提示词模板
PROMPT_TEMPLATES = {
    "daily_inspiration": "搜索 AI 领域最新进展，找出 3 个值得写的选题，每个选题用一句话说明为什么值得写",
    "hot_topic": "搜索 '{topic}' 最新进展，找出 3 个还未被大量写过、但很有讨论价值的新角度",
    "competitor_monitor": "搜索 '{company}' 最新动态，包括：① 新动作 ② 核心产品 ③ 媒体报道 ④ 困难",
    "industry_tracking": "搜索 '{industry}' 赛道最新动态，包括：① 融资事件 ② 头部公司新产品 ③ 重大收购 ④ 政策变化",
}


def search_tavily(query: str, **kwargs) -> Dict[str, Any]:
    """
    使用 Tavily AI 搜索

    Args:
        query: 搜索查询
        **kwargs: 额外参数
            - search_depth: 搜索深度（basic/advanced/comprehensive）
            - max_results: 最大结果数
            - include_domains: 包含的域名列表
            - days: 搜索时间范围（1-7 天）
            - topic: 搜索主题（如 "news", "finance"）

    Returns:
        搜索结果字典
    """

    # 检查 API Key
    if not TAVILYLY_API_KEY or TAVILYLY_API_KEY == 'your_key_here':
        return {
            "success": False,
            "error": "TAVILLYLY_API_KEY 未配置",
            "help": "请先在环境变量中配置 TAVILLYLY_API_KEY"
        }

    # 构建请求
    payload = {
        "query": query,
        **DEFAULT_CONFIG,
        **kwargs
    }

    headers = {
        'Content-Type': 'application/json',
        'API-Key': TAVILLYLY_API_KEY,
    }

    try:
        response = requests.post(
            TAVILLY_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        return {
            "success": True,
            "query": query,
            "results": data.get('results', []),
            "answer": data.get('answer', ''),
            "usage": data.get('usage', {}),
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "help": "请求失败，请检查 API Key 或网络连接"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"未知错误: {str(e)}",
            "help": "请检查网络连接或联系管理员"
        }


def format_results(results: List[Dict[str, Any]]) -> str:
    """
    格式化搜索结果为 Markdown

    Args:
        results: 搜索结果列表

    Returns:
        Markdown 格式的字符串
    """

    if not results:
        return "未找到相关结果"

    output = f"## 搜索结果（{len(results)} 条）\n\n"

    for i, result in enumerate(results, 1):
        title = result.get('title', '无标题')
        url = result.get('url', '无链接')
        snippet = result.get('content', '无摘要')

        output += f"### {i}. {title}\n"
        output += f"**来源**: {result.get('source', '未知')}\n"
        output += f"**链接**: {url}\n"
        output += f"**摘要**: {snippet[:200]}...\n\n"

    return output


def get_daily_inspiration() -> str:
    """
    获取每日选题灵感

    Returns:
        Markdown 格式的选题列表
    """

    prompt = PROMPT_TEMPLATES['daily_inspiration']
    result = search_tavily(prompt)

    if not result['success']:
        return f"❌ 搜索失败: {result['error']}"

    return format_results(result['results'])


def get_hot_topic(topic: str) -> str:
    """
    获取热点话题最新进展

    Returns:
        Markdown 格式的进展列表
    """

    prompt = PROMPT_TEMPLATES['hot_topic'].format(topic=topic)
    result = search_tavily(prompt)

    if not result['success']:
        return f"❌ 搜索失败: {result['error']}"

    return format_results(result['results'])


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("用法: python tavily_search.py <搜索查询>")
        sys.exit(1)

    query = ' '.join(sys.argv[1:])
    result = search_tavily(query)

    if result['success']:
        print("✅ 搜索成功！\n")
        print(format_results(result['results']))
    else:
        print(f"❌ 搜索失败: {result['error']}")
        print(f"帮助: {result.get('help', '无')}")
