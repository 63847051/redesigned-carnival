#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竞品信息抓取脚本
抓取竞品官网的关键信息并保存为 JSON
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), '../config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def scrape_page(url, config):
    """抓取单个页面"""
    headers = {
        'User-Agent': config['scraping_rules']['user_agent']
    }
    
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=config['scraping_rules']['timeout']
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取基本信息
        title = soup.find('title')
        title = title.get_text().strip() if title else "无标题"
        
        # 提取主要内容
        content = soup.get_text()[:500]  # 前 500 字符
        
        # 提取价格（如果有）
        price = None
        price_elements = soup.find_all(class_=lambda x: x and ('price' in x.lower() or 'pricing' in x.lower()))
        if price_elements:
            price = price_elements[0].get_text().strip()
        
        return {
            'url': url,
            'title': title,
            'content': content,
            'price': price,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def scrape_competitor(competitor, config):
    """抓取单个竞品的所有页面"""
    results = []
    
    for page in competitor['pages']:
        print(f"正在抓取: {competitor['name']} - {page['name']}")
        result = scrape_page(page['url'], config)
        result['competitor'] = competitor['name']
        result['page_type'] = page['type']
        results.append(result)
        
        # 延迟，避免请求过快
        import time
        time.sleep(config['scraping_rules']['delay_between_requests'])
    
    return results

def main():
    """主函数"""
    print("🚀 开始抓取竞品信息...")
    
    # 加载配置
    config = load_config()
    
    # 创建数据目录
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    os.makedirs(data_dir, exist_ok=True)
    
    # 抓取所有竞品
    all_results = []
    for competitor in config['competitors']:
        print(f"\n📊 抓取竞品: {competitor['name']}")
        results = scrape_competitor(competitor, config)
        all_results.extend(results)
    
    # 保存结果
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(data_dir, f'{today}.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 抓取完成！")
    print(f"📁 文件保存到: {output_file}")
    print(f"📊 共抓取 {len(all_results)} 个页面")
    
    # 统计
    success_count = len([r for r in all_results if 'error' not in r])
    error_count = len([r for r in all_results if 'error' in r])
    
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {error_count}")
    
    return output_file

if __name__ == '__main__':
    main()
