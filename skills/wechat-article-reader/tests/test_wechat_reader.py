#!/usr/bin/env python3
"""
Unit tests for WeChat Article Reader
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wechat_article_reader import WeChatArticleReader


class TestWeChatArticleReader(unittest.TestCase):
    """Test cases for WeChatArticleReader"""

    def setUp(self):
        """Set up test fixtures"""
        self.reader = WeChatArticleReader()

    def test_valid_wechat_url(self):
        """Test URL validation"""
        # Valid URLs
        self.assertTrue(self.reader.is_valid_wechat_url(
            'https://mp.weixin.qq.com/s/XXXXX'
        ))
        self.assertTrue(self.reader.is_valid_wechat_url(
            'https://mp.weixin.qq.com/s?__biz=123&mid=456&sn=789'
        ))

        # Invalid URLs
        self.assertFalse(self.reader.is_valid_wechat_url(
            'https://weixin.qq.com/...'
        ))
        self.assertFalse(self.reader.is_valid_wechat_url(
            'https://mp.weixin.qq.com/cgi-bin/...'
        ))

    def test_normalize_url(self):
        """Test URL normalization"""
        # HTTP to HTTPS
        self.assertEqual(
            self.reader.normalize_url('http://mp.weixin.qq.com/s/XXXXX'),
            'https://mp.weixin.qq.com/s/XXXXX'
        )

        # Strip whitespace
        self.assertEqual(
            self.reader.normalize_url('  https://mp.weixin.qq.com/s/XXXXX  '),
            'https://mp.weixin.qq.com/s/XXXXX'
        )

    def test_clean_content(self):
        """Test content cleaning"""
        # Remove extra whitespace
        cleaned = self.reader.clean_content('Line 1\n\n\nLine 2')
        self.assertEqual(cleaned, 'Line 1\n\nLine 2')

        # Remove special characters
        cleaned = self.reader.clean_content('Text\x00with\x08special\x1fchars')
        self.assertEqual(cleaned, 'Textwithspecialchars')

    def test_to_markdown(self):
        """Test Markdown conversion"""
        result = {
            'title': 'Test Title',
            'author': 'Test Author',
            'publish_time': '2024-03-15',
            'url': 'https://example.com',
            'content': 'Test content',
            'word_count': 12,
            'method': 'iPhone UA',
        }

        md = self.reader.to_markdown(result)
        self.assertIn('# Test Title', md)
        self.assertIn('**Author**: Test Author', md)
        self.assertIn('Test content', md)
        self.assertIn('Word count: 12', md)

    def test_invalid_url_raises_error(self):
        """Test that invalid URL raises ValueError"""
        with self.assertRaises(ValueError):
            self.reader.extract_with_ua('https://invalid-url.com')


class TestExtractionMethods(unittest.TestCase):
    """Test extraction methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.reader = WeChatArticleReader()

    def test_session_reuse(self):
        """Test session cookie reuse"""
        # This test requires actual cookies
        cookies = {
            'test_cookie': 'test_value'
        }

        # Note: This will fail with actual URL without valid cookies
        # This is just to test the method exists
        self.assertTrue(hasattr(self.reader, 'extract_with_session'))

    def test_batch_extraction(self):
        """Test batch extraction with rate limiting"""
        # Mock URLs for testing
        urls = [
            'https://mp.weixin.qq.com/s/test1',
            'https://mp.weixin.qq.com/s/test2',
        ]

        # This will fail with invalid URLs, but tests the structure
        try:
            results = self.reader.extract_batch(urls, delay=0.1)
            self.assertIsInstance(results, list)
        except Exception as e:
            # Expected to fail with invalid URLs
            self.assertIn('Invalid WeChat article URL', str(e))


if __name__ == '__main__':
    unittest.main()
