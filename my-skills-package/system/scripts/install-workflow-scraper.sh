#!/bin/bash
# 工作流助手 - 集成Scrapling数据采集
# 大领导 🎯

WORKSPACE="/root/.openclaw/workspace"
PYTHON_SCRIPT="$WORKSPACE/scripts/workflow-scraper.py"

# 创建Python脚本
cat > "$PYTHON_SCRIPT" << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
"""
工作流数据采集助手
使用Scrapling抓取网页数据
"""

import sys
import json
from scrapling.fetchers import Fetcher

def scrape_url(url, css_selector=None):
    """
    抓取URL内容
    
    Args:
        url: 目标URL
        css_selector: CSS选择器（可选）
    
    Returns:
        抓取的数据
    """
    try:
        print(f"🕷️ 正在抓取: {url}")
        
        # 抓取网页
        page = Fetcher.get(url)
        
        # 提取数据
        if css_selector:
            data = page.css(css_selector).getall()
        else:
            # 默认提取body内容
            data = page.css('body ::text').getall()
        
        print(f"✅ 成功抓取 {len(data)} 条数据")
        return data
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        return []

def scrape_feishu_wiki(url):
    """
    抓取飞书知识库
    
    Args:
        url: 飞书知识库URL
    
    Returns:
        内容列表
    """
    print(f"📝 正在抓取飞书知识库: {url}")
    
    try:
        page = Fetcher.get(url)
        
        # 提取内容
        content = {
            'title': page.css('h1::text').get() or '',
            'text': page.css('body ::text').getall(),
            'links': page.css('a::attr(href)').getall()
        }
        
        print(f"✅ 成功抓取飞书知识库")
        return content
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        return {}

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  抓取URL: python3 workflow-scraper.py <url>")
        print("  抓取飞书: python3 workflow-scraper.py --feishu <url>")
        print("  提取元素: python3 workflow-scraper.py <url> <css_selector>")
        return
    
    url = sys.argv[1]
    
    # 判断命令类型
    if '--feishu' in sys.argv:
        # 抓取飞书
        result = scrape_feishu_wiki(url)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif len(sys.argv) >= 3:
        # 带选择器抓取
        css_selector = sys.argv[2]
        result = scrape_url(url, css_selector)
        for item in result:
            print(f"  - {item}")
    
    else:
        # 简单抓取
        result = scrape_url(url)
        for item in result[:10]:  # 只显示前10条
            print(f"  - {item}")

if __name__ == '__main__':
    main()
PYTHON_SCRIPT

chmod +x "$PYTHON_SCRIPT"

echo "✅ 工作流数据采集助手已创建"
echo ""
echo "📖 使用方法:"
echo ""
echo "1. 抓取网页内容:"
echo "   python3 $PYTHON_SCRIPT <url>"
echo ""
echo "2. 抓取飞书知识库:"
echo "   python3 $PYTHON_SCRIPT --feishu <飞书URL>"
echo ""
echo "3. 提取特定元素:"
echo "   python3 $PYTHON_SCRIPT <url> <css选择器>"
echo ""
echo "🎯 示例:"
echo "   python3 $PYTHON_SCRIPT https://example.com"
echo "   python3 $PYTHON_SCRIPT https://example.com '.content'"
echo "   python3 $PYTHON_SCRIPT --feishu https://ux7aumj3ud.feishu.cn/wiki/..."
echo ""
