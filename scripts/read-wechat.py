#!/usr/bin/env python3
"""
微信文章快速读取工具
使用 iPhone User-Agent 绕过反爬虫
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
from datetime import datetime

def read_wechat_article(url):
    """读取微信文章"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取元数据
        title = soup.find('meta', property='og:title')
        desc = soup.find('meta', property='og:description')
        
        # 提取内容
        content_div = soup.find('div', id='js_content')
        
        if content_div:
            # 移除脚本和样式
            for script in content_div(['script', 'style']):
                script.decompose()
            
            # 提取文本
            text = content_div.get_text('\n', strip=True)
            
            # 清理多余空行
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            return {
                'success': True,
                'title': title.get('content') if title else '未知标题',
                'description': desc.get('content') if desc else '',
                'content': text,
                'length': len(text)
            }
        else:
            return {
                'success': False,
                'error': '未找到文章内容，可能被反爬虫拦截'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法: python3 read-wechat.py <微信文章URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    result = read_wechat_article(url)
    
    if result['success']:
        print(f"✅ 成功读取文章")
        print(f"📝 标题: {result['title']}")
        print(f"📄 内容长度: {result['length']} 字符")
        print(f"\n{'='*60}")
        print(result['content'])
    else:
        print(f"❌ 读取失败: {result['error']}")
        sys.exit(1)
