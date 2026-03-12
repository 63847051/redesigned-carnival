#!/usr/bin/env python3
"""
工作流数据采集助手 v2.0
集成Scrapling到日常工作流
"""

import sys
import json
from datetime import datetime
from scrapling.fetchers import Fetcher

def scrape_public_data(url):
    """抓取公开网页数据"""
    try:
        print(f"🕷️ 正在抓取: {url}")
        page = Fetcher.get(url)
        
        # 提取标题
        title = page.css('title::text').get() or '无标题'
        
        # 提取正文
        content = page.css('p::text').getall()
        
        # 提取所有链接
        links = page.css('a::attr(href)').getall()
        
        result = {
            'url': url,
            'title': title,
            'content': content[:20],  # 前20段
            'links_count': len(links),
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ 成功抓取: {title}")
        print(f"   内容段数: {len(content)}")
        print(f"   链接数: {len(links)}")
        
        return result
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        return None

def scrape_product_page(url):
    """抓取产品页面"""
    try:
        print(f"📦 正在抓取产品页: {url}")
        page = Fetcher.get(url)
        
        # 提取产品信息
        products = []
        
        for item in page.css('.product, .item'):
            product = {
                'name': item.css('.name, .title::text').get(),
                'price': item.css('.price::text').get(),
                'description': item.css('.desc::text').get()
            }
            if product['name']:
                products.append(product)
        
        print(f"✅ 成功抓取 {len(products)} 个产品")
        
        return products
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        return []

def scrape_news_site(url):
    """抓取新闻网站"""
    try:
        print(f"📰 正在抓取新闻: {url}")
        page = Fetcher.get(url)
        
        # 提取新闻条目
        news_items = []
        
        for item in page.css('.article, .news-item'):
            news = {
                'title': item.css('h2, h3::text').get(),
                'summary': item.css('.summary::text').get(),
                'link': item.css('a::attr(href)').get()
            }
            if news['title']:
                news_items.append(news)
        
        print(f"✅ 成功抓取 {len(news_items)} 条新闻")
        
        return news_items
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        return []

def save_to_json(data, filename):
    """保存数据到JSON文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 数据已保存到: {filename}")
    except Exception as e:
        print(f"❌ 保存失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 60)
        print("🕷️ 工作流数据采集助手 v2.0")
        print("=" * 60)
        print()
        print("使用方法:")
        print()
        print("1. 抓取公开网页:")
        print("   python3 workflow-scraper.py public <url>")
        print()
        print("2. 抓取产品页面:")
        print("   python3 workflow-scraper.py product <url>")
        print()
        print("3. 抓取新闻网站:")
        print("   python3 workflow-scraper.py news <url>")
        print()
        print("4. 保存到文件:")
        print("   python3 workflow-scraper.py public <url> --output data.json")
        print()
        print("🎯 示例:")
        print("   python3 workflow-scraper.py public https://example.com")
        print("   python3 workflow-scraper.py product https://shop.com/products")
        print("   python3 workflow-scraper.py news https://news.com")
        print()
        print("=" * 60)
        return
    
    command = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else None
    output = None
    
    # 检查是否有--output参数
    if '--output' in sys.argv:
        output_idx = sys.argv.index('--output')
        if output_idx + 1 < len(sys.argv):
            output = sys.argv[output_idx + 1]
    
    if not url:
        print("❌ 错误: 请提供URL")
        return
    
    # 执行命令
    if command == 'public':
        result = scrape_public_data(url)
        if output and result:
            save_to_json(result, output)
    
    elif command == 'product':
        result = scrape_product_page(url)
        if output and result:
            save_to_json(result, output)
    
    elif command == 'news':
        result = scrape_news_site(url)
        if output and result:
            save_to_json(result, output)
    
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == '__main__':
    main()
