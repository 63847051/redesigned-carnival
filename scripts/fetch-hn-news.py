#!/usr/bin/env python3
"""
Fetch AI-related news from Hacker News front page
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def fetch_hn_ai_news():
    """Fetch and parse Hacker News front page for AI-related news"""
    url = "https://news.ycombinator.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw-Bot/1.0)'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'llm', 'gpt', 'chatgpt', 'claude', 'openai',
            'transformer', 'diffusion', 'stable diffusion', 'agent', 'agentic',
            'embedding', 'rag', 'fine-tuning', 'inference', 'training'
        ]

        news_items = []
        rows = soup.find_all('tr', class_='athing')

        for row in rows[:30]:  # Check first 30 items
            title_elem = row.find('span', class_='titleline')
            if not title_elem:
                continue

            link_elem = title_elem.find('a')
            if not link_elem:
                continue

            title = link_elem.get_text()
            href = link_elem.get('href', '')

            # Check if title or link contains AI keywords
            title_lower = title.lower()
            is_ai_related = any(keyword in title_lower for keyword in ai_keywords)

            if is_ai_related:
                # Get the item ID for HN link
                item_id = row.get('id')
                hn_link = f"https://news.ycombinator.com/item?id={item_id}" if item_id else url

                news_items.append({
                    'title': title,
                    'link': href if href.startswith('http') else hn_link,
                    'hn_link': hn_link
                })

                if len(news_items) >= 10:
                    break

        return news_items

    except Exception as e:
        print(f"Error fetching HN: {e}")
        return []

def format_news_md(news_items, date_str):
    """Format news items as markdown"""
    md_content = f"""# AI News from Hacker News

**Date**: {date_str}
**Source**: https://news.ycombinator.com
**Count**: {len(news_items)} items

---

"""

    for i, item in enumerate(news_items, 1):
        md_content += f"## {i}. {item['title']}\n\n"
        md_content += f"- **Link**: {item['link']}\n"
        md_content += f"- **HN Discussion**: {item['hn_link']}\n\n"

    return md_content

if __name__ == "__main__":
    date_str = datetime.now().strftime("%Y-%m-%d")
    news = fetch_hn_ai_news()

    if news:
        md_content = format_news_md(news, date_str)
        print(md_content)
    else:
        print("No AI-related news found or error occurred.")
