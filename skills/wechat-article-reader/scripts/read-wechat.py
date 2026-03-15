#!/usr/bin/env python3
"""
Quick WeChat Article Extractor - Command-line tool

Usage:
    python read-wechat.py <url>
    python read-wechat.py <url> --output article.md
    python read-wechat.py <url> --screenshot
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wechat_article_reader import WeChatArticleReader


def main():
    if len(sys.argv) < 2:
        print("Usage: python read-wechat.py <url> [--output file.md] [--screenshot]")
        sys.exit(1)

    url = sys.argv[1]
    output_file = None
    screenshot = False

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--screenshot':
            screenshot = True
            i += 1
        else:
            i += 1

    try:
        print(f"🔍 Extracting: {url}")
        reader = WeChatArticleReader()
        result = reader.extract_with_ua(url)

        print(f"\n✅ Success!")
        print(f"📰 Title: {result['title']}")
        print(f"👤 Author: {result['author']}")
        print(f"🕐 Publish Time: {result['publish_time']}")
        print(f"📊 Word Count: {result['word_count']}")
        print(f"🛠️ Method: {result['method']}")

        # Show content preview
        content_preview = result['content'][:200] + '...' if len(result['content']) > 200 else result['content']
        print(f"\n📝 Content Preview:")
        print(content_preview)

        # Save to file
        if output_file:
            reader.to_markdown(result, output_file)
            print(f"\n💾 Saved to: {output_file}")

        # Screenshot
        if screenshot:
            print("\n📸 Screenshot feature requires Selenium setup")
            print("Install: pip install selenium")
            print("Then install Chrome/Chromium browser")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
