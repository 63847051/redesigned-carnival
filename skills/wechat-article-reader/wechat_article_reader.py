#!/usr/bin/env python3
"""
WeChat Article Reader - Extract content from WeChat Official Account articles

This module provides methods to bypass WeChat's anti-bot detection and extract
full article content including metadata.
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse


class WeChatArticleReader:
    """Extract content from WeChat Official Account articles"""

    # iPhone User-Agent (bypasses most anti-bot checks)
    IPHONE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.15(0x18000f2f) NetType/WIFI Language/zh_CN'

    def __init__(self, session: Optional[requests.Session] = None):
        """
        Initialize the reader

        Args:
            session: Optional requests.Session for reuse
        """
        self.session = session or requests.Session()
        self.last_url = None
        self.last_result = None

    def is_valid_wechat_url(self, url: str) -> bool:
        """
        Check if URL is a valid WeChat article link

        Args:
            url: URL to validate

        Returns:
            True if valid WeChat article URL
        """
        return 'mp.weixin.qq.com' in url and ('/s/' in url or '__biz=' in url)

    def normalize_url(self, url: str) -> str:
        """
        Normalize URL to HTTPS format

        Args:
            url: URL to normalize

        Returns:
            Normalized URL
        """
        url = url.strip()
        if url.startswith('http://'):
            url = url.replace('http://', 'https://', 1)
        return url

    def extract_with_ua(self, url: str) -> Dict:
        """
        Extract article using iPhone User-Agent

        Args:
            url: WeChat article URL

        Returns:
            Dictionary with article data

        Raises:
            ValueError: If URL is invalid
            requests.RequestException: If request fails
        """
        if not self.is_valid_wechat_url(url):
            raise ValueError(f"Invalid WeChat article URL: {url}")

        url = self.normalize_url(url)

        headers = {
            'User-Agent': self.IPHONE_UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        response = self.session.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract metadata
        title_meta = soup.find('meta', property='og:title')
        author_meta = soup.find('meta', property='og:article:author')
        desc_meta = soup.find('meta', property='og:description')

        # Extract content
        content_div = soup.find('div', id='js_content')
        if not content_div:
            raise ValueError("Content not found - article may be protected or deleted")

        # Extract publish time
        publish_time_elem = soup.find('em', class_='rich_media_meta_text')
        publish_time = publish_time_elem.text if publish_time_elem else ""

        # Get main content text
        content_text = content_div.get_text('\n', strip=True)

        result = {
            'title': title_meta['content'] if title_meta else '',
            'author': author_meta['content'] if author_meta else '',
            'description': desc_meta['content'] if desc_meta else '',
            'publish_time': publish_time,
            'content': self.clean_content(content_text),
            'url': url,
            'word_count': len(content_text),
            'method': 'iPhone UA',
        }

        self.last_url = url
        self.last_result = result

        return result

    def extract_with_session(self, url: str, cookies: Dict) -> Dict:
        """
        Extract article using session cookies

        Args:
            url: WeChat article URL
            cookies: Dictionary of cookies to use

        Returns:
            Dictionary with article data
        """
        for key, value in cookies.items():
            self.session.cookies.set(key, value, domain='mp.weixin.qq.com')

        return self.extract_with_ua(url)

    def clean_content(self, text: str) -> str:
        """
        Clean and format article content

        Args:
            text: Raw content text

        Returns:
            Cleaned content
        """
        # Remove extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Remove special characters
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        # Remove common WeChat artifacts
        text = re.sub(r'本文转载自.*', '', text)
        text = re.sub(r'长按识别.*', '', text)
        return text.strip()

    def to_markdown(self, result: Dict, filename: Optional[str] = None) -> str:
        """
        Convert article result to Markdown format

        Args:
            result: Article result dictionary
            filename: Optional filename to save

        Returns:
            Markdown content
        """
        md_content = f"""# {result['title']}

**Author**: {result['author']}
**Publish Time**: {result['publish_time']}
**URL**: {result['url']}

---

{result['content']}

---

*Extracted by WeChat Article Reader*
*Word count: {result['word_count']}*
"""

        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(md_content)

        return md_content

    def extract_batch(self, urls: list, delay: float = 2.0) -> list:
        """
        Extract multiple articles with rate limiting

        Args:
            urls: List of WeChat article URLs
            delay: Delay between requests (seconds)

        Returns:
            List of article results
        """
        results = []
        for i, url in enumerate(urls):
            try:
                result = self.extract_with_ua(url)
                results.append(result)
                print(f"✅ [{i+1}/{len(urls)}] {result['title'][:50]}")

                if i < len(urls) - 1:
                    time.sleep(delay)
            except Exception as e:
                print(f"❌ [{i+1}/{len(urls)}] Failed: {e}")
                results.append({'url': url, 'error': str(e)})

        return results


def extract_article(url: str, method: str = 'auto') -> Dict:
    """
    Convenience function to extract a WeChat article

    Args:
        url: WeChat article URL
        method: Extraction method ('auto', 'ua', 'session')

    Returns:
        Dictionary with article data
    """
    reader = WeChatArticleReader()

    if method == 'auto' or method == 'ua':
        return reader.extract_with_ua(url)
    elif method == 'session':
        raise ValueError("Session method requires cookies parameter")
    else:
        raise ValueError(f"Unknown method: {method}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python wechat_article_reader.py <url> [--output file.md]")
        sys.exit(1)

    url = sys.argv[1]
    output_file = None

    if len(sys.argv) > 2 and sys.argv[2] == '--output':
        output_file = sys.argv[3]

    try:
        result = extract_article(url)
        print(f"✅ Extracted: {result['title']}")
        print(f"👤 Author: {result['author']}")
        print(f"📝 {result['word_count']} words")

        if output_file:
            reader = WeChatArticleReader()
            reader.to_markdown(result, output_file)
            print(f"💾 Saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
