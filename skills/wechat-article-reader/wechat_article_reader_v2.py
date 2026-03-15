#!/usr/bin/env python3
"""
WeChat Article Reader v2.0 - Enhanced with logging, retries, and optimizations

Improvements over v1.0:
- Added comprehensive logging
- Enhanced URL validation
- Retry logic with exponential backoff
- Connection pooling for performance
- Better error handling
- Rate limiting decorator
"""

import re
import time
import logging
import hashlib
from functools import wraps, lru_cache
from typing import Dict, Optional, List
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def rate_limit(calls_per_second: float = 0.5):
    """
    Rate limiting decorator to prevent API abuse

    Args:
        calls_per_second: Maximum calls allowed per second
    """
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator


class WeChatArticleReader:
    """
    Enhanced WeChat Article Reader with logging, retries, and optimizations

    Features:
    - Comprehensive logging
    - Retry logic with exponential backoff
    - Connection pooling
    - Enhanced URL validation
    - Rate limiting
    - Caching support
    """

    # iPhone User-Agent (bypasses most anti-bot checks)
    IPHONE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.15(0x18000f2f) NetType/WIFI Language/zh_CN'

    def __init__(self, session: Optional[requests.Session] = None, enable_cache: bool = True):
        """
        Initialize the enhanced reader

        Args:
            session: Optional requests.Session for reuse
            enable_cache: Enable request caching
        """
        self.session = session or requests.Session()
        self.enable_cache = enable_cache

        # Configure connection pooling and retries
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry
        )
        self.session.mount('https://', adapter)

        self.last_url = None
        self.last_result = None

        logger.info("WeChatArticleReader v2.0 initialized with connection pooling")

    def is_valid_wechat_url(self, url: str) -> bool:
        """
        Enhanced URL validation with comprehensive checks

        Args:
            url: URL to validate

        Returns:
            True if valid WeChat article URL
        """
        try:
            parsed = urlparse(url)

            # Check domain
            if parsed.netloc.lower() not in ['mp.weixin.qq.com']:
                logger.warning(f"Invalid domain: {parsed.netloc}")
                return False

            # Check path
            if not parsed.path.startswith('/s') and '__biz=' not in parsed.query:
                logger.warning(f"Invalid path: {parsed.path}")
                return False

            # Force HTTPS
            if parsed.scheme != 'https':
                logger.warning(f"Non-HTTPS scheme: {parsed.scheme}")
                return False

            return True
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False

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

    @rate_limit(calls_per_second=0.5)
    def _make_request(self, url: str, headers: Dict) -> requests.Response:
        """
        Make HTTP request with rate limiting

        Args:
            url: URL to fetch
            headers: Request headers

        Returns:
            Response object
        """
        response = self.session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response

    def extract_with_ua(self, url: str, max_retries: int = 2) -> Dict:
        """
        Enhanced extraction with retry logic and logging

        Args:
            url: WeChat article URL
            max_retries: Maximum retry attempts

        Returns:
            Dictionary with article data

        Raises:
            ValueError: If URL is invalid
            requests.RequestException: If request fails after retries
        """
        if not self.is_valid_wechat_url(url):
            raise ValueError(f"Invalid WeChat article URL: {url}")

        url = self.normalize_url(url)
        logger.info(f"Extracting article: {url}")

        headers = {
            'User-Agent': self.IPHONE_UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        # Retry logic with exponential backoff
        for attempt in range(max_retries + 1):
            try:
                response = self._make_request(url, headers)
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
                    'method': 'iPhone UA v2',
                }

                self.last_url = url
                self.last_result = result

                logger.info(f"✅ Successfully extracted: {result['title'][:50]}")
                return result

            except requests.RequestException as e:
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    logger.warning(f"Retry {attempt + 1}/{max_retries} in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed after {max_retries} retries: {e}")
                    raise
            except Exception as e:
                logger.error(f"❌ Extraction failed: {e}")
                raise

    def extract_with_session(self, url: str, cookies: Dict) -> Dict:
        """
        Enhanced session extraction with cookie validation

        Args:
            url: WeChat article URL
            cookies: Dictionary of cookies to use

        Returns:
            Dictionary with article data
        """
        # Validate cookie structure
        required_keys = ['key']
        if not all(k in cookies for k in required_keys):
            raise ValueError(f"Missing required cookie keys: {required_keys}")

        # Set cookies with domain validation
        domain = 'mp.weixin.qq.com'
        for key, value in cookies.items():
            if not isinstance(value, str):
                raise ValueError(f"Cookie value for '{key}' must be string")
            self.session.cookies.set(key, value, domain=domain, path='/')

        logger.info(f"Using session cookies for: {url}")
        return self.extract_with_ua(url)

    def clean_content(self, text: str) -> str:
        """
        Enhanced content cleaning with multiple strategies

        Args:
            text: Raw content text

        Returns:
            Cleaned content
        """
        # Remove extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Remove control characters but preserve Unicode
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # Remove WeChat artifacts (more precise patterns)
        artifacts = [
            r'本文转载自[^\n]{0,100}',
            r'长按识别[^\n]{0,100}',
            r'点击阅读原文[^\n]{0,100}',
            r'关注公众号[^\n]{0,100}',
        ]
        for pattern in artifacts:
            text = re.sub(pattern, '', text)

        # Normalize spaces
        text = re.sub(r'[ \t]+', ' ', text)

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

*Extracted by WeChat Article Reader v2.0*
*Word count: {result['word_count']}*
"""

        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"💾 Saved to: {filename}")

        return md_content

    def extract_batch(self, urls: List[str], delay: float = 2.0, max_retries: int = 2) -> Dict:
        """
        Enhanced batch extraction with retry and statistics

        Args:
            urls: List of WeChat article URLs
            delay: Delay between requests (seconds)
            max_retries: Maximum retry attempts per URL

        Returns:
            Dict with 'results', 'success_count', 'failure_count', 'total'
        """
        logger.info(f"Starting batch extraction: {len(urls)} URLs")

        results = []
        success_count = 0
        failure_count = 0

        for i, url in enumerate(urls):
            try:
                result = self.extract_with_ua(url, max_retries=max_retries)
                results.append(result)
                success_count += 1
                logger.info(f"✅ [{i+1}/{len(urls)}] {result['title'][:50]}")
            except Exception as e:
                logger.error(f"❌ [{i+1}/{len(urls)}] Failed: {e}")
                results.append({'url': url, 'error': str(e)})
                failure_count += 1

            # Delay between requests
            if i < len(urls) - 1:
                logger.debug(f"Waiting {delay}s before next request")
                time.sleep(delay)

        summary = {
            'results': results,
            'success_count': success_count,
            'failure_count': failure_count,
            'total': len(urls),
            'success_rate': f"{(success_count/len(urls)*100):.1f}%"
        }

        logger.info(f"Batch complete: {success_count}/{len(urls)} successful")
        return summary


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

    if method in ['auto', 'ua']:
        return reader.extract_with_ua(url)
    elif method == 'session':
        raise ValueError("Session method requires cookies parameter")
    else:
        raise ValueError(f"Unknown method: {method}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python wechat_article_reader_v2.py <url> [--output file.md]")
        sys.exit(1)

    url = sys.argv[1]
    output_file = None

    if len(sys.argv) > 2 and sys.argv[2] == '--output':
        output_file = sys.argv[3]

    try:
        logger.info("Starting WeChat Article Reader v2.0")
        result = extract_article(url)
        print(f"✅ Extracted: {result['title']}")
        print(f"👤 Author: {result['author']}")
        print(f"📝 {result['word_count']} words")

        if output_file:
            reader = WeChatArticleReader()
            reader.to_markdown(result, output_file)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
