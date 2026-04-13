#!/usr/bin/env python3
"""
采集 Hacker News 的 AI 相关新闻
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# AI 相关的关键词
AI_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'ml',
    'deep learning', 'neural network', 'llm', 'gpt', 'chatgpt',
    'openai', 'anthropic', 'claude', 'gemini', 'transformer',
    'diffusion', 'stable diffusion', 'midjourney', 'huggingface',
    'tensorflow', 'pytorch', 'nlp', 'computer vision', 'cv',
    'reinforcement learning', 'robotics', 'automation', 'agent'
]

def fetch_hacker_news():
    """获取 Hacker News 首页"""
    url = 'https://news.ycombinator.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text

def parse_news(html):
    """解析新闻列表"""
    soup = BeautifulSoup(html, 'html.parser')
    news_items = []
    
    # 找到所有新闻行
    news_rows = soup.find_all('tr', class_='athing')
    
    for row in news_rows[:30]:  # 先获取前30条，后面筛选
        title_cell = row.find('span', class_='titleline')
        if not title_cell:
            continue
            
        title_link = title_cell.find('a')
        if not title_link:
            continue
            
        title = title_link.get_text()
        url = title_link.get('href', '')
        
        # 检查是否是 AI 相关
        title_lower = title.lower()
        is_ai_related = any(keyword in title_lower for keyword in AI_KEYWORDS)
        
        if is_ai_related:
            # 获取新闻元信息（分数、评论数等）
            next_row = row.find_next_sibling('tr')
            subtext = next_row.find('td', class_='subtext')
            
            score = 0
            comments = 0
            
            if subtext:
                score_span = subtext.find('span', class_='score')
                if score_span:
                    score_text = score_span.get_text()
                    score = int(re.search(r'\d+', score_text).group())
                
                comment_links = subtext.find_all('a')
                for link in comment_links:
                    if 'comment' in link.get_text().lower():
                        comment_text = link.get_text()
                        match = re.search(r'\d+', comment_text)
                        if match:
                            comments = int(match.group())
                            break
            
            news_items.append({
                'title': title,
                'url': url,
                'score': score,
                'comments': comments
            })
            
            if len(news_items) >= 10:
                break
    
    return news_items

def save_news(news_items, output_path):
    """保存新闻到文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f'# AI News from Hacker News\n\n')
        f.write(f'**采集时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC\n')
        f.write(f'**来源**: https://news.ycombinator.com\n')
        f.write(f'**数量**: {len(news_items)} 条\n\n')
        f.write('---\n\n')
        
        for i, item in enumerate(news_items, 1):
            f.write(f'## {i}. {item["title"]}\n\n')
            f.write(f'- **链接**: {item["url"]}\n')
            f.write(f'- **分数**: {item["score"]} points\n')
            f.write(f'- **评论**: {item["comments"]} comments\n\n')

def main():
    try:
        print('📡 正在获取 Hacker News...')
        html = fetch_hacker_news()
        
        print('🔍 正在解析 AI 相关新闻...')
        news_items = parse_news(html)
        
        if not news_items:
            print('⚠️  未找到 AI 相关新闻')
            return
        
        output_path = '/root/.openclaw/workspace/data/ai-news-20260404.md'
        save_news(news_items, output_path)
        
        print(f'✅ 成功采集 {len(news_items)} 条 AI 相关新闻')
        print(f'📄 保存到: {output_path}')
        
        # 打印简要预览
        print('\n📰 新闻预览:')
        for i, item in enumerate(news_items, 1):
            print(f'{i}. {item["title"]}')
        
    except Exception as e:
        print(f'❌ 采集失败: {e}')
        raise

if __name__ == '__main__':
    main()
