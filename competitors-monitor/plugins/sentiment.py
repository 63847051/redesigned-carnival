#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户舆情监控插件
监控社交媒体舆情，进行情感分析
"""

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any


class SentimentAnalyzer:
    """简单的情感分析器"""

    def __init__(self):
        self.positive_words = [
            "好",
            "棒",
            "赞",
            "优秀",
            "喜欢",
            "满意",
            "推荐",
            "感谢",
            "good",
            "great",
            "excellent",
            "amazing",
            "love",
            "best",
            "perfect",
        ]
        self.negative_words = [
            "差",
            "烂",
            "糟",
            "失望",
            "投诉",
            "骗",
            "bug",
            "崩溃",
            "闪退",
            "bad",
            "terrible",
            "awful",
            "hate",
            "worst",
            "bug",
            "crash",
            "scam",
        ]

    def analyze(self, text: str) -> float:
        """分析文本情感，返回 -1 到 1 之间的分数"""
        if not text:
            return 0.0

        text_lower = text.lower()

        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)

        total = positive_count + negative_count
        if total == 0:
            return 0.0

        score = (positive_count - negative_count) / total
        return max(-1.0, min(1.0, score))

    def get_sentiment_label(self, score: float) -> str:
        """获取情感标签"""
        if score > 0.3:
            return "positive"
        elif score < -0.3:
            return "negative"
        else:
            return "neutral"


class SocialMediaPlugin:
    """社交媒体数据源插件"""

    def __init__(self):
        try:
            import requests
            from bs4 import BeautifulSoup

            self.requests = requests
            self.BeautifulSoup = BeautifulSoup
        except ImportError:
            raise ImportError("请安装依赖: pip3 install requests beautifulsoup4")

        self.analyzer = SentimentAnalyzer()

    def fetch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取社交媒体数据"""
        results = []

        sources = config.get("data_sources", {})

        if sources.get("rss_feed", {}).get("enabled"):
            rss_data = self._fetch_rss(config)
            results.extend(rss_data)

        if sources.get("twitter", {}).get("enabled"):
            twitter_data = self._fetch_twitter(config)
            results.extend(twitter_data)

        if sources.get("news_api", {}).get("enabled"):
            news_data = self._fetch_news(config)
            results.extend(news_data)

        if sources.get("mock", {}).get("enabled"):
            mock_data = self._generate_mock_data(config)
            results.extend(mock_data)

        for item in results:
            if "content" in item or "title" in item:
                text = item.get("content", "") or item.get("title", "")
                sentiment_score = self.analyzer.analyze(text)
                item["sentiment_score"] = sentiment_score
                item["sentiment"] = self.analyzer.get_sentiment_label(sentiment_score)

        return results

    def _fetch_rss(self, config: Dict[str, Any]) -> List[Dict]:
        """获取 RSS 订阅源"""
        results = []

        rss_config = config.get("data_sources", {}).get("rss_feed", {})
        feeds = rss_config.get("feeds", [])

        for feed_url in feeds:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = self.requests.get(feed_url, headers=headers, timeout=30)
                response.raise_for_status()

                soup = self.BeautifulSoup(response.text, "xml")
                items = soup.find_all("item")[:10]

                for item in items:
                    title = item.find("title")
                    description = item.find("description")
                    link = item.find("link")

                    results.append(
                        {
                            "source": "rss",
                            "type": "news",
                            "title": title.get_text().strip() if title else "",
                            "content": description.get_text().strip()[:500]
                            if description
                            else "",
                            "url": link.get_text().strip() if link else "",
                            "published": item.find("pubDate").get_text()
                            if item.find("pubDate")
                            else "",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

            except Exception as e:
                results.append(
                    {
                        "source": "rss",
                        "error": str(e),
                        "url": feed_url,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return results

    def _fetch_twitter(self, config: Dict[str, Any]) -> List[Dict]:
        """获取 Twitter 数据"""
        twitter_config = config.get("data_sources", {}).get("twitter", {})
        bearer_token = twitter_config.get("bearer_token")

        if not bearer_token or bearer_token == "YOUR_TWITTER_BEARER_TOKEN":
            return [
                {
                    "source": "twitter",
                    "error": "未配置 Twitter Bearer Token",
                    "timestamp": datetime.now().isoformat(),
                }
            ]

        return [
            {
                "source": "twitter",
                "error": "需配置 Twitter API v2",
                "timestamp": datetime.now().isoformat(),
            }
        ]

    def _fetch_news(self, config: Dict[str, Any]) -> List[Dict]:
        """获取新闻 API 数据"""
        news_config = config.get("data_sources", {}).get("news_api", {})
        api_key = news_config.get("api_key")

        if not api_key or api_key == "YOUR_NEWS_API_KEY":
            return [
                {
                    "source": "news_api",
                    "error": "未配置 News API Key",
                    "timestamp": datetime.now().isoformat(),
                }
            ]

        return [
            {
                "source": "news_api",
                "error": "需配置 News API",
                "timestamp": datetime.now().isoformat(),
            }
        ]

    def _generate_mock_data(self, config: Dict[str, Any]) -> List[Dict]:
        """生成模拟数据用于测试"""
        targets = config.get("targets", [])
        keywords = []
        if targets:
            keywords = targets[0].get("keywords", ["产品"])

        mock_posts = [
            {"content": f"{keywords[0]}真好用，非常推荐！", "interactions": 50},
            {"content": f"{keywords[0]}体验很差，客服态度不好", "interactions": 30},
            {"content": f"{keywords[0]}新品发布会很精彩", "interactions": 100},
            {"content": f"{keywords[0]}有bug，经常崩溃", "interactions": 20},
            {"content": f"期待{keywords[0]}下一代产品", "interactions": 15},
        ]

        results = []
        for i, post in enumerate(mock_posts):
            results.append(
                {
                    "source": "mock",
                    "type": "social_post",
                    "content": post["content"],
                    "interactions": post["interactions"],
                    "platform": "weibo",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return results

    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据"""
        return len(data) > 0


class SentimentMonitor:
    """舆情监控器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.plugin = SocialMediaPlugin()

    def fetch(self) -> List[Dict[str, Any]]:
        """抓取数据"""
        return self.plugin.fetch(self.config)

    def analyze(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析舆情数据"""
        alerts = []
        check_rules = self.config.get("check_rules", {})

        negative_posts = [d for d in data if d.get("sentiment") == "negative"]
        positive_posts = [d for d in data if d.get("sentiment") == "positive"]
        neutral_posts = [d for d in data if d.get("sentiment") == "neutral"]

        if negative_posts:
            for post in negative_posts:
                alerts.append(
                    {
                        "type": "negative_sentiment",
                        "severity": "warning",
                        "source": post.get("source"),
                        "content": post.get("content", post.get("title", ""))[:100],
                        "sentiment_score": post.get("sentiment_score"),
                        "message": f"检测到负面舆情: {post.get('content', '')[:50]}...",
                    }
                )

        total_interactions = sum(d.get("interactions", 0) for d in data)
        if total_interactions > 1000:
            alerts.append(
                {
                    "type": "viral_post",
                    "severity": "info",
                    "total_interactions": total_interactions,
                    "message": f"舆情热度较高，总互动量: {total_interactions}",
                }
            )

        return alerts

    def generate_report(self, data: List[Dict], alerts: List[Dict]) -> str:
        """生成舆情报告"""
        report = "## 📊 舆情监控报告\n\n"

        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for item in data:
            sentiment = item.get("sentiment", "neutral")
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

        report += "### 情感分布\n\n"
        report += f"- 正面: {sentiment_counts['positive']} 条\n"
        report += f"- 负面: {sentiment_counts['negative']} 条\n"
        report += f"- 中性: {sentiment_counts['neutral']} 条\n\n"

        if alerts:
            report += "### ⚠️ 告警\n\n"
            for alert in alerts:
                emoji = "🔴" if alert["severity"] == "warning" else "🟡"
                report += f"{emoji} {alert['message']}\n"

        return report


def run_monitor():
    """运行舆情监控"""
    import sys

    config_path = "config/sentiment.json"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    monitor = SentimentMonitor(config)
    data = monitor.fetch()
    alerts = monitor.analyze(data)

    print(f"获取到 {len(data)} 条舆情数据")
    print(f"发现 {len(alerts)} 条告警")

    report = monitor.generate_report(data, alerts)
    print("\n" + report)

    return data, alerts


if __name__ == "__main__":
    run_monitor()
