#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竞品变化检测脚本
对比今天和昨天的数据，识别变化
"""

import json
import os
from datetime import datetime, timedelta
import difflib

def load_json(file_path):
    """加载 JSON 文件"""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_latest_data(data_dir):
    """获取最新的数据文件"""
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    today_file = os.path.join(data_dir, f'{today}.json')
    yesterday_file = os.path.join(data_dir, f'{yesterday}.json')
    
    today_data = load_json(today_file)
    yesterday_data = load_json(yesterday_file)
    
    return today_data, yesterday_data, today, yesterday

def compare_text(text1, text2):
    """对比两段文本的差异"""
    if not text1 or not text2:
        return None
    
    # 计算相似度
    seq = difflib.SequenceMatcher(None, text1, text2)
    similarity = seq.ratio()
    
    # 如果相似度小于 0.9，认为有变化
    if similarity < 0.9:
        # 生成差异
        diff = list(difflib.unified_diff(
            text1.splitlines(keepends=True),
            text2.splitlines(keepends=True),
            fromfile='yesterday',
            tofile='today',
            lineterm=''
        ))
        return {
            'similarity': similarity,
            'diff': ''.join(diff)
        }
    
    return None

def compare_price(price1, price2):
    """对比价格"""
    if not price1 or not price2:
        return None
    
    if price1 != price2:
        return {
            'old': price1,
            'new': price2
        }
    
    return None

def detect_changes(today_data, yesterday_data):
    """检测变化"""
    if not yesterday_data:
        return {
            'type': 'first_run',
            'message': '首次运行，没有历史数据对比'
        }
    
    changes = []
    
    # 构建昨天的数据字典（按 URL）
    yesterday_dict = {}
    for item in yesterday_data:
        key = f"{item['competitor']}_{item['page_type']}"
        yesterday_dict[key] = item
    
    # 对比今天的数据
    for item in today_data:
        key = f"{item['competitor']}_{item['page_type']}"
        
        # 检查是否是新页面
        if key not in yesterday_dict:
            changes.append({
                'type': 'new',
                'competitor': item['competitor'],
                'page_type': item['page_type'],
                'url': item['url'],
                'title': item.get('title'),
                'message': f"新增页面: {item['competitor']} - {item['page_type']}"
            })
        else:
            # 对比现有页面
            yesterday_item = yesterday_dict[key]
            
            # 检查标题变化
            if item.get('title') != yesterday_item.get('title'):
                changes.append({
                    'type': 'updated',
                    'field': 'title',
                    'competitor': item['competitor'],
                    'page_type': item['page_type'],
                    'url': item['url'],
                    'old': yesterday_item.get('title'),
                    'new': item.get('title'),
                    'message': f"标题变化: {item['competitor']} - {item['page_type']}"
                })
            
            # 检查内容变化
            content_diff = compare_text(yesterday_item.get('content', ''), item.get('content', ''))
            if content_diff:
                changes.append({
                    'type': 'updated',
                    'field': 'content',
                    'competitor': item['competitor'],
                    'page_type': item['page_type'],
                    'url': item['url'],
                    'similarity': content_diff['similarity'],
                    'diff': content_diff['diff'][:500],  # 只保留前 500 字符
                    'message': f"内容变化: {item['competitor']} - {item['page_type']} (相似度: {content_diff['similarity']:.2%})"
                })
            
            # 检查价格变化
            price_diff = compare_price(yesterday_item.get('price'), item.get('price'))
            if price_diff:
                changes.append({
                    'type': 'updated',
                    'field': 'price',
                    'competitor': item['competitor'],
                    'page_type': item['page_type'],
                    'url': item['url'],
                    'old_price': price_diff['old'],
                    'new_price': price_diff['new'],
                    'message': f"价格变化: {item['competitor']} - {item['page_type']}"
                })
    
    # 检查删除的页面
    for key, item in yesterday_dict.items():
        found = False
        for today_item in today_data:
            if f"{today_item['competitor']}_{today_item['page_type']}" == key:
                found = True
                break
        
        if not found:
            changes.append({
                'type': 'deleted',
                'competitor': item['competitor'],
                'page_type': item['page_type'],
                'url': item['url'],
                'message': f"删除页面: {item['competitor']} - {item['page_type']}"
            })
    
    return changes

def save_changes(changes, data_dir, today):
    """保存变化数据"""
    output_file = os.path.join(data_dir, f'diff-{today}.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(changes, f, ensure_ascii=False, indent=2)
    
    return output_file

def main():
    """主函数"""
    print("🔍 开始检测竞品变化...")
    
    # 获取数据目录
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    
    # 加载今天和昨天的数据
    today_data, yesterday_data, today, yesterday = get_latest_data(data_dir)
    
    if not today_data:
        print("❌ 找不到今天的数据文件")
        print("💡 请先运行抓取脚本: python3 scripts/scrape.py")
        return
    
    print(f"📅 今天: {today}")
    print(f"📅 昨天: {yesterday}")
    
    # 检测变化
    changes = detect_changes(today_data, yesterday_data)
    
    # 如果是首次运行
    if isinstance(changes, dict) and changes.get('type') == 'first_run':
        print(f"⚠️  {changes['message']}")
        print("💡 明天将开始检测变化")
        return
    
    # 保存变化
    output_file = save_changes(changes, data_dir, today)
    
    # 统计变化
    new_count = len([c for c in changes if c['type'] == 'new'])
    updated_count = len([c for c in changes if c['type'] == 'updated'])
    deleted_count = len([c for c in changes if c['type'] == 'deleted'])
    
    print(f"\n✅ 变化检测完成！")
    print(f"📊 变化统计:")
    print(f"  ➕ 新增: {new_count}")
    print(f"  🔄 更新: {updated_count}")
    print(f"  ➖ 删除: {deleted_count}")
    print(f"📁 文件保存到: {output_file}")
    
    # 显示具体变化
    if changes:
        print(f"\n📋 变化详情:")
        for change in changes[:10]:  # 只显示前 10 个
            print(f"  {change['message']}")
        
        if len(changes) > 10:
            print(f"  ... 还有 {len(changes) - 10} 个变化")
    else:
        print(f"\n✨ 没有检测到变化")
    
    return output_file

if __name__ == '__main__':
    main()
